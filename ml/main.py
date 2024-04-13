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
)

from dataset import DataProcess, SignalProcess
from model import Model, CatBoost
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
    def __init__(self, model: Model, data_process: DataProcess) -> None:
        super().__init__()

        self._model = model
        self._data_process = data_process

    async def detect_frame_anomaly(
        self, url: str, tmpdirname: str, idx: int, fps: int, query_id: int
    ) -> dict:
        bin_path = save_bin(url, tmpdirname, idx, fps)
        X = self._data_process.prepare_from_bin(bin_path).to_numpy()
        label = self._model.predict(X)[0]

        if label == "normal":
            return {}

        label = self._model.decode_label(label)[0]

        print(f"Anomaly detected at {idx} with label {label}")

        producer = aiokafka.AIOKafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_HOST"),
            value_serializer=lambda x: json.dumps(x).encode(encoding="utf-8"),
            acks="all",
            enable_idempotence=True,
        )
        await producer.start()
        try:
            async with aiofiles.open(bin_path, "rb") as bin_f:
                data = await bin_f.read()
                data = base64.b64encode(data).decode("utf-8")
                await producer.send_and_wait(
                    "anomalies",
                    {
                        "idx": idx,
                        "cls": label,
                        "fps": fps,
                        "query_id": query_id,
                        "data": data,
                    },
                )
        finally:
            await producer.stop()

        return {"ts": idx, "class": label}

    async def Process(self, query: Query, context: grpc.aio.ServicerContext):
        print(query.source)

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
                    return Response(status=ResponseStatus.Canceled)

                try:
                    anomaly = await self.detect_frame_anomaly(
                        url, str(tmpdirname), idx, fps, query.id
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

        anomalies = (
            mongo_client.get_database(os.getenv("MONGO_DB"))
            .get_collection("anomalies")
            .find({"query_id": query.id})
        )

        for anomaly in anomalies:
            a = Anomaly(ts=anomaly["ts"], cls=anomaly["cls"])

            links = []
            for i in range(anomaly["cnt"]):
                links.append(
                    s3.presigned_get_object(
                        "detection-frame", f"{query.id}/{anomaly['ts']}_{i}.jpg"
                    )
                )
            a.links.extend(links)
            res.append(a)

        return ResultResp(anomalies=res)


async def serve():
    checkpoint_path = "./cb_checkpoint"

    model = CatBoost()
    model.load(checkpoint_path)
    data_process = SignalProcess()

    s = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    pb.detection_pb2_grpc.add_MlServiceServicer_to_server(
        MlService(model, data_process), s
    )
    s.add_insecure_port("[::]:10000")

    await s.start()
    await s.wait_for_termination()
    await s.stop(5)


if __name__ == "__main__":
    asyncio.run(serve())
