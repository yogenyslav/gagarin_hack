import asyncio
import tempfile
import os
from concurrent import futures

import ffmpeg
import grpc
import minio
import pb.detection_pb2_grpc
from dotenv import load_dotenv
from grpc import ServicerContext

from pb.detection_pb2 import Query, Response, ResponseStatus, ResultReq, ResultResp

from dataset import DataProcess, SignalProcess
from model import LogReg, Model
from video import save_bin


load_dotenv('.env')

s3 = minio.Minio(
    "s3.larek.tech",
    access_key=os.getenv('ACCESS_KEY'),
    secret_key=os.getenv('SECRET_KEY'),
    secure=True,
)


class MlService(pb.detection_pb2_grpc.MlServiceServicer):
    def __init__(self, model: Model, data_process: DataProcess) -> None:
        super().__init__()

        self._model = model
        self._data_process = data_process

    def detect_frame_anomaly(
        self, url: str, tmpdirname: str, idx: int, fps: int
    ) -> dict:
        bin_path = save_bin(url, tmpdirname, idx, fps)
        X = self._data_process.prepare_from_bin(bin_path).to_numpy()
        label = self._model.predict(X)[0]

        if label == 0:
            return {}

        label = self._model.decode_label(label)

        return {"ts": idx, "class": label}

    async def Process(self, query: Query, context: grpc.aio.ServicerContext):
        print(query.source)

        url = s3.presigned_get_object("detection-video", query.source)
        print(f"url = {url}")

        probe = ffmpeg.probe(url)
        video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")
        fps = video_info["r_frame_rate"].split("/")
        fps = int(fps[0])//int(fps[1])
        num_frames = int(video_info["nb_frames"])
        frames_to_read = list(range(num_frames // fps - 1))

        tmpdirname = tempfile.TemporaryDirectory()

        anomalies = []  # list[ {"ts": int, 'class': str}, ... ]

        with tempfile.TemporaryDirectory() as tmpdirname:
            for idx in frames_to_read:
                if context.cancelled():
                    return Response(status=ResponseStatus.Canceled)

                try:
                    anomaly = self.detect_frame_anomaly(url, str(tmpdirname), idx, fps)
                except Exception as ex:
                    print(str(ex))
                    return Response(status=ResponseStatus.Error)

                if not anomaly:
                    continue

                anomalies.append(anomaly)

            # tmpdirname.cleanup()

        # TODO add rtsp stream

        return Response(status=ResponseStatus.Success)

    def FindResult(self, query: ResultReq, context: ServicerContext):
        return ResultResp(anomalies=[])


async def serve():
    checkpoint_path = "/home/fromy/projects/gaga/gagarin_hack/ml/checkpoint"

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


if __name__ == "__main__":
    asyncio.run(serve())
