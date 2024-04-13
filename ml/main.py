import asyncio
import pb.detection_pb2_grpc
import grpc
import minio
from pb.detection_pb2 import Query, Response, ResponseStatus, ResultReq, ResultResp
from grpc import ServicerContext
from concurrent import futures


# s3 = minio.Minio(
#     "minio:9000",
#     access_key="UpD4O18jra6OzxQ1n7P7",
#     secret_key="gco0w8pUu62pwuV6ZmOyfT0ScJFE2e2jiaEqpuDC",
#     secure=False,
# )

# if not s3.bucket_exists("frame"):
#     s3.make_bucket("frame", "eu-west-1", True)


class MlService(pb.detection_pb2_grpc.MlServiceServicer):
    async def Process(self, query: Query, context: grpc.aio.ServicerContext):
        print(query)
        return Response(status=ResponseStatus.Success)

    def FindResult(self, query: ResultReq, context: ServicerContext):

        return ResultResp(anomalies=[])


async def serve():
    s = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    pb.detection_pb2_grpc.add_MlServiceServicer_to_server(MlService(), s)
    s.add_insecure_port("[::]:10000")

    await s.start()
    await s.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
