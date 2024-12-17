import asyncio
import aioredis
import yaml
import json
import logging
from pathlib import Path


# 로깅 설정
logging.basicConfig(
    filename="redis_cluster.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# YAML 설정 파일 로드
CONFIG_PATH = Path(__file__).parent / "configs/database.yaml"
with open(CONFIG_PATH, "r") as file:
    config: list[dict[str, str | int]] = yaml.safe_load(file)["redis_clusters"]

# Redis 클러스터 비동기 관리자
class RedisManager:
    """
    Redis 클러스터를 비동기적으로 관리하는 클래스
    """

    def __init__(self):
        """
        Redis 클라이언트 초기화
        """
        self.startup_nodes: list[dict[str, str | int]] = config

    async def get_client(self, port: int) -> aioredis.Redis:
        """
        특정 노드에 연결하는 비동기 클라이언트 생성
        Args:
            port (int): 노드의 포트 번호
        Returns:
            aioredis.Redis: 비동기 Redis 클라이언트
        """
        node = next((n for n in self.startup_nodes if n["port"] == port), None)
        if not node:
            raise ValueError(f"❌ 포트 {port}에 해당하는 노드가 없습니다.")
        return await aioredis.from_url(f"redis://{node['host']}:{node['port']}")

    async def store_data(self, port: int, key: str, value: str | dict):
        """
        비동기적으로 데이터를 특정 Redis 노드에 저장
        Args:
            port (int): 저장할 노드의 포트 번호
            key (str): 저장할 키
            value (str | dict): 저장할 값 (문자열 또는 딕셔너리)
        """
        client = await self.get_client(port)
        try:
            serialized_value = json.dumps(value) if isinstance(value, dict) else value
            await client.set(key, serialized_value)
            logging.info(f"✅ {key} → {port}번 노드에 저장됨.")
            print(f"✅ '{key}' → {port}번 노드에 저장됨.")
        except Exception as e:
            logging.error(f"❌ 데이터 저장 실패 (포트 {port}, 키: {key}): {e}")
            print(f"❌ 데이터 저장 실패: {e}")
        finally:
            await client.close()

    async def fetch_data(self, port: int, key: str):
        """
        비동기적으로 데이터를 특정 Redis 노드에서 조회
        Args:
            port (int): 조회할 노드의 포트 번호
            key (str): 조회할 키
        Returns:
            str | dict | None: 조회된 값
        """
        client = await self.get_client(port)
        try:
            value = await client.get(key)
            if value:
                try:
                    return json.loads(value)  # JSON 직렬화된 값을 딕셔너리로 반환
                except json.JSONDecodeError:
                    return value  # 일반 문자열 반환
            return None
        except Exception as e:
            logging.error(f"❌ 데이터 조회 실패 (포트 {port}, 키: {key}): {e}")
            print(f"❌ 데이터 조회 실패: {e}")
            return None
        finally:
            await client.close()

# 비동기 실행
async def main():
    manager = RedisClusterManager()

    # 테스트 키워드 데이터
    test_data = [
        {"port": 7000, "key": "keyword_7000", "value": {"message": "Data for port 7000"}},
        {"port": 7001, "key": "keyword_7001", "value": "Simple string for port 7001"},
        {"port": 7002, "key": "keyword_7002", "value": {"info": "More data for 7002"}},
    ]

    # 비동기 저장 작업 (동시 실행)
    tasks = [manager.store_data(data["port"], data["key"], data["value"]) for data in test_data]
    await asyncio.gather(*tasks)

    # 비동기 조회 작업 (동시 실행)
    tasks = [manager.fetch_data(data["port"], data["key"]) for data in test_data]
    results = await asyncio.gather(*tasks)

    # 결과 출력
    for data, result in zip(test_data, results):
        print(f"📖 조회된 데이터: '{data['key']}' → {result}")

if __name__ == "__main__":
    print("🔄 Redis Cluster 비동기 테스트 시작...")
    asyncio.run(main())
    print("✅ Redis Cluster 비동기 테스트 완료.")