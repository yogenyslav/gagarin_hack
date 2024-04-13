import tempfile
import os
from concurrent import futures

import ffmpeg
import grpc
import pb.detection_pb2_grpc
from dotenv import load_dotenv
from grpc import ServicerContext

from pb.detection_pb2 import (
    Query,
    Response,
    ResponseStatus,
    ResultReq,
    ResultResp,
    Anomaly,
)

from dataset import DataProcess, SignalProcess
from model import LogReg, Model
from video import save_bin

from miniopy_async import Minio
import pymongo
import cv2
import aiofiles
import asyncio
import acapture


load_dotenv(".env")

s3 = Minio(
    os.getenv("S3_HOST"),
    access_key=os.getenv("ACCESS_KEY"),
    secret_key=os.getenv("SECRET_KEY"),
    secure=True,
)

mongo_client = pymongo.MongoClient(
    f"mongodb://{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/{os.getenv('MONGO_DB')}"
)


class MlService(pb.detection_pb2_grpc.MlServiceServicer):
    def __init__(self, model: Model, data_process: DataProcess) -> None:
        super().__init__()

        self._model = model
        self._data_process = data_process

    async def _save_frame(
        self,
        bin_path: str,
        tmpdirname: str,
        idx: int,
        query_id: int,
        fps: int,
        label: str,
    ):
        async with aiofiles.open(bin_path, "rb") as bin_f:
            data = await bin_f.read()
            async with aiofiles.open(
                f"{tmpdirname}/anomaly_frames_{query_id}.h264", "wb"
            ) as f:
                await f.write(data)

            cap = acapture.open(f"{tmpdirname}/anomaly_frames_{query_id}.h264")
            cnt = 0
            while cnt <= fps:
                _, raw = cap.read()
                frame = cv2.cvtColor(raw, cv2.IMREAD_COLOR)
                img_bytes = cv2.imencode(".jpg", frame)[1].tobytes()
                await s3.put_object(
                    "detection-frame",
                    f"{query_id}/{idx}_{cnt}.jpg",
                    img_bytes,
                    length=len(img_bytes),
                    content_type="image/jpeg",
                )
                cnt += 1

        mongo_client.get_database(os.getenv("MONGO_DB")).get_collection(
            "anomalies"
        ).insert_one(
            {
                "query_id": query_id,
                "ts": idx,
                "cls": label,
                "cnt": cnt,
            }
        )

    async def detect_frame_anomaly(
        self, url: str, tmpdirname: str, idx: int, fps: int, query_id: int
    ) -> dict:
        bin_path = save_bin(url, tmpdirname, idx, fps)
        X = self._data_process.prepare_from_bin(bin_path).to_numpy()
        label = self._model.predict(X)[0]

        if label == 0:
            return {}

        label = self._model.decode_label(label)

        await asyncio.create_task(
            self._save_frame(bin_path, tmpdirname, idx, query_id, fps, label)
        )

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
                if context.is_active():
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

        return Response(status=ResponseStatus.Success)

    async def FindResult(self, query: ResultReq, context: grpc.aio.ServicerContext):
        res: list[Anomaly] = []

        anomalies = (
            mongo_client.get_database(os.getenv("MONGO_DB"))
            .get_collection("anomalies")
            .find({"query_id": query.id})
        )

        for anomaly in anomalies:
            a = Anomaly(ts=anomaly["ts"], cls=anomaly["class"])

            links = []
            for i in range(anomaly["cnt"]):
                await links.append(
                    s3.presigned_get_object(
                        "detection-frame", f"{query.id}/{anomaly['ts']}_{i}.jpg"
                    )
                )
            a.links.extend(links)
            res.append(a)

        return ResultResp(anomalies=res)


async def serve():
    checkpoint_path = "./checkpoint"

    model = LogReg()
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
