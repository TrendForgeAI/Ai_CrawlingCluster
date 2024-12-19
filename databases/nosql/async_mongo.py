from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
import yaml


class MongoDBAsync:
    def __init__(self, uri, db_name) -> None:
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    async def insert_data(self, collection_name, data):
        collection = self.db[collection_name]
        result = await collection.insert_one(data)
        return result.inserted_id

    async def close(self):
        self.client.close()


async def mongo_main(data: list, table: str) -> None:
    keyword_yaml_path = Path(__file__).parent / "configs/cy/database.yaml"
    with open(keyword_yaml_path, "r", encoding="utf-8") as file:
        data: dict = yaml.safe_load(file)["mongo_db"]

    # MongoDB URI와 데이터베이스 이름
    uri = data["host"]  # 자신의 MongoDB URI로 변경
    db_name = "crawling_data_insert_db"

    # MongoDBAsync 인스턴스 생성
    mongo = MongoDBAsync(uri, db_name)

    # 데이터 삽입
    inserted_id = await mongo.insert_data(f"{table}_collection", data)
    print(f"Inserted document ID: {inserted_id}")

    # 연결 종료
    await mongo.close()
