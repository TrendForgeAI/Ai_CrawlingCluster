import redis
import yaml
import json
import logging
from pathlib import Path
from typing import Union, List
from redis.cluster import ClusterNode

# 로깅 설정
logging.basicConfig(
    filename="redis_cluster.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# YAML 설정 파일 로드
CONFIG_PATH = Path(__file__).parent.parent.parent / "configs/cy/database.yaml"
with open(CONFIG_PATH, "r") as file:
    config: List[dict] = yaml.safe_load(file)


# Redis 클러스터 관리자
class RedisClusterManager:
    """
    Redis 클러스터를 동기식으로 관리하는 클래스
    """

    def __init__(self) -> None:
        """
        Redis 클러스터 클라이언트 초기화
        """
        # Redis 클러스터 노드 설정
        self.startup_nodes: list[ClusterNode] = [
            ClusterNode(host=node["host"], port=node["port"])
            for node in config["redis_clusters"]
        ]
        self.cluster_client = redis.RedisCluster(
            startup_nodes=self.startup_nodes, decode_responses=True
        )
        self.node_clients = {
            node["host"]: redis.StrictRedis(
                host=node["host"], port=node["port"], decode_responses=True
            )
            for node in config["redis_clusters"]
        }
        print("🚀 Redis 클러스터 모드 활성화")

    def store_data(self, key: str, value: Union[str, dict], port: int | None = None):
        """
        데이터를 Redis 클러스터에 저장. 특정 포트에 저장할 수 있음.
        Args:
            key (str): 저장할 키
            value (Union[str, dict]): 저장할 값
            port (Optional[int]): 특정 노드의 포트 번호 (None이면 자동 분산)
        """
        try:
            serial_value: str = json.dumps(value) if isinstance(value, dict) else value

            if port:
                # 특정 노드에 저장
                if port not in self.node_clients:
                    raise ValueError(
                        f"❌ 지정된 포트 {port}에 해당하는 노드가 없습니다."
                    )
                client = self.node_clients[port]
                client.set(key, serial_value)
                logging.info(f"✅ {key} → {port}번 노드에 저장됨.")
            else:
                # 클러스터 자동 분산 저장
                self.cluster_client.set(key, serial_value)
                logging.info(f"✅ {key} → Redis 클러스터에 자동 저장됨.")

        except Exception as e:
            logging.error(f"❌ 데이터 저장 실패 (키: {key}, 포트: {port}): {e}")
            print(f"❌ 데이터 저장 실패: {e}")

    def fetch_data(self, key: str, port: int | None = None) -> Union[str, dict, None]:
        """
        데이터를 Redis 클러스터에서 조회. 특정 포트에서 조회 가능.
        Args:
            key (str): 조회할 키
            port (Optional[int]): 특정 노드의 포트 번호 (None이면 클러스터에서 조회)
        Returns:
            Union[str, dict, None]: 조회된 값
        """
        try:
            if self.cluster_client.cluster_nodes():
                if port:
                    # 특정 노드에서 데이터 조회
                    if port not in self.node_clients:
                        raise ValueError(
                            f"❌ 지정된 포트 {port}에 해당하는 노드가 없습니다."
                        )
                    client = self.node_clients[port]
                    value = client.get(key)
                else:
                    # 클러스터 자동 조회
                    value = self.cluster_client.get(key)

                if value:
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
                return None
        except Exception as e:
            logging.error(f"❌ 데이터 조회 실패 (키: {key}, 포트: {port}): {e}")
            print(f"❌ 데이터 조회 실패: {e}")
            return None
