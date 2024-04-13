import aiokafka
import asyncio
import os
import pymongo
import cv2
import numpy as np
import json
import tempfile
import base64
from minio import Minio
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO


load_dotenv(".env")


mongo_url = f"mongodb://{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/{os.getenv('MONGO_DB')}"
print(f"mongo_url = {mongo_url}")
mongo_client = pymongo.MongoClient(mongo_url)
col = mongo_client.get_database(os.getenv("MONGO_DB")).get_collection("anomalies")

s3 = Minio(
    os.getenv("S3_HOST"),
    access_key=os.getenv("ACCESS_KEY"),
    secret_key=os.getenv("SECRET_KEY"),
    secure=True,
)


async def main():
    consumer = aiokafka.AIOKafkaConsumer(
        "anomalies",
        bootstrap_servers=os.getenv("KAFKA_HOST"),
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    await consumer.start()
    try:
        async for msg in consumer:
            with tempfile.TemporaryDirectory() as tmpdirname:
                print(f"Received message: {msg.offset} {msg.key}")
                idx = msg.value["idx"]
                fps = msg.value["fps"]
                query_id = msg.value["query_id"]
                label = msg.value["cls"]
                data = base64.b64decode(msg.value["data"])

                with open(f"{tmpdirname}/anomaly_frames_{query_id}.h264", "wb") as f:
                    f.write(data)

                cap = cv2.VideoCapture(f"{tmpdirname}/anomaly_frames_{query_id}.h264")
                cnt = 0
                total_frames_uploaded = 0
                print(f"fps = {fps}")
                while cnt < fps - 1:
                    _, raw = cap.read()
                    # if cnt == 0 or cnt == fps - 2 or cnt == (fps - 1) // 2:
                    frame = cv2.cvtColor(raw, cv2.IMREAD_COLOR)
                    img = np.array(
                        Image.open(BytesIO(cv2.imencode(".jpg", frame)[1].tobytes()))
                    )
                    data = BytesIO()
                    Image.fromarray(img).save(data, "JPEG")
                    data.seek(0)
                    s3.put_object(
                        "detection-frame",
                        f"{query_id}/{idx}_{total_frames_uploaded}.jpg",
                        data,
                        length=len(data.getvalue()),
                        content_type="image/jpeg",
                    )
                    print(f"Uploaded {query_id}/{idx}_{total_frames_uploaded}.jpg")
                    total_frames_uploaded += 1
                    cnt += 1

                col.insert_one(
                    {
                        "query_id": query_id,
                        "ts": idx,
                        "cls": label,
                        "cnt": total_frames_uploaded,
                    }
                )
                print(f"Inserted anomaly {query_id}/{idx}_{total_frames_uploaded}")

    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
