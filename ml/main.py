import tempfile
import os
from concurrent import futures

import ffmpeg
import grpc
import pb.detection_pb2_grpc
from dotenv import load_dotenv

from pb.detection_pb2 import (
    Query,
    Response,
    ResponseStatus,
    ResultReq,
    ResultResp,
    Anomaly,
    Model as ModelChoice,
)

from dataset import DataProcess, SignalProcess, ResNetProcess
from model import Model, CatBoost, DLModel
from video import save_bin

from minio import Minio
import pymongo
import aiokafka
import asyncio
import json
import aiofiles
import base64


load_dotenv(".env")

s3 = Minio(
    os.getenv("S3_HOST"),
    access_key=os.getenv("ACCESS_KEY"),
    secret_key=os.getenv("SECRET_KEY"),
    secure=True,
)

mongo_url = f"mongodb://{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/{os.getenv('MONGO_DB')}"
mongo_client = pymongo.MongoClient(mongo_url)
col = mongo_client.get_database(os.getenv("MONGO_DB")).get_collection("anomalies")


class MlService(pb.detection_pb2_grpc.MlServiceServicer):
    def __init__(
        self,
        model_rgb: Model,
        model_bytes: Model,
        data_process_rgb: ResNetProcess,
        data_process_bytes: DataProcess,
    ) -> None:
        super().__init__()

        self._model_rgb = model_rgb
        self._model_bytes = model_bytes
        self._data_process_rgb = data_process_rgb
        self._data_process_bytes = data_process_bytes
        self.producer = aiokafka.AIOKafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_HOST"),
            value_serializer=lambda x: json.dumps(x).encode(encoding="utf-8"),
            acks="all",
            enable_idempotence=True,
        )

    async def detect_frame_anomaly(
        self,
        url: str,
        tmpdirname: str,
        idx: int,
        fps: int,
        query_id: int,
        model_choice: str,
    ) -> dict:
        bin_path = save_bin(url, tmpdirname, idx, fps)

        X = (
            self._data_process_bytes.prepare_from_bin(bin_path).to_numpy()
            if model_choice == "Bytes"
            else self._data_process_rgb.prepare_from_bin(bin_path)
        )

        label = (
            self._model_bytes.predict(X)[0]
            if model_choice == "Bytes"
            else self._model_rgb.predict(X)[0]
        )

        if label == "normal":
            return {}

        print(f"Anomaly detected at {idx} with label {label}")

        async with aiofiles.open(bin_path, "rb") as bin_f:
            data = await bin_f.read()
            data = base64.b64encode(data).decode("utf-8")
            await self.producer.send_and_wait(
                "anomalies",
                {
                    "idx": idx,
                    "cls": label,
                    "fps": fps,
                    "query_id": query_id,
                    "data": data,
                },
            )

        return {"ts": idx, "class": label}

    async def Process(self, query: Query, context: grpc.aio.ServicerContext):
        print(query.source)
        model_choice = "Rgb" if query.model == ModelChoice.Rgb else "Bytes"
        url = query.source
        if not query.source.startswith("rtsp"):
            url = s3.presigned_get_object("detection-video", query.source)
        print(f"url = {url}")

        probe = ffmpeg.probe(url)
        video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")
        fps = video_info["r_frame_rate"].split("/")
        fps = int(fps[0]) // int(fps[1])
        num_frames = int(video_info["nb_frames"])
        frames_to_read = list(range(num_frames // fps - 1))

        tmpdirname = tempfile.TemporaryDirectory()

        anomalies = []  # list[ {"ts": int, 'class': str}, ... ]

        with tempfile.TemporaryDirectory() as tmpdirname:
            for idx in frames_to_read:
                if context.cancelled():
                    print("cancelled")
                    return Response(status=ResponseStatus.Canceled)

                try:
                    anomaly = await self.detect_frame_anomaly(
                        url,
                        str(tmpdirname),
                        idx,
                        fps,
                        query.id,
                        model_choice,
                    )
                except Exception as ex:
                    print(str(ex))
                    return Response(status=ResponseStatus.Error)

                if not anomaly:
                    continue

                anomalies.append(anomaly)

            # tmpdirname.cleanup()
        print("finished processing")
        return Response(status=ResponseStatus.Success)

    async def FindResult(self, query: ResultReq, context: grpc.aio.ServicerContext):
        res: list[Anomaly] = []
        try:
            anomalies = col.find({"query_id": query.id})
            for anomaly in anomalies:
                a = Anomaly(
                    ts=anomaly["ts"], cls=anomaly["cls"], links=anomaly["links"]
                )
                res.append(a)
            return ResultResp(anomalies=res)
        except Exception as e:
            print(e)
            return ResultResp(anomalies=[])


async def serve():
    cb_checkpoint_path = "./cb_checkpoint"
    resnet_checkpoint_path = "./resnet_checkpoint"

    cb_model = CatBoost()
    cb_model.load(cb_checkpoint_path)
    cb_data_process = SignalProcess()

    resnet_model = DLModel()
    resnet_model.load(resnet_checkpoint_path)
    resnet_data_process = ResNetProcess()

    s = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    ml_service = MlService(resnet_model, cb_model, resnet_data_process, cb_data_process)
    pb.detection_pb2_grpc.add_MlServiceServicer_to_server(ml_service, s)
    s.add_insecure_port("[::]:10000")

    await ml_service.producer.start()
    await s.start()
    await s.wait_for_termination()
    await s.stop(5)
    await ml_service.producer.stop()


if __name__ == "__main__":
    asyncio.run(serve())
