import redis
import yaml
import json
import logging
from pathlib import Path
from redis.cluster import ClusterNode
from dataclasses import dataclass

# 로깅 설정
logging.basicConfig(
    filename="redis_cluster.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# YAML 설정 파일 로드
CONFIG_PATH = Path(__file__).parent.parent.parent / "configs/cy/database.yaml"
with open(CONFIG_PATH, "r") as file:
    config: dict = yaml.safe_load(file)


@dataclass
class RedisNode:
    """Redis 노드 정보를 담는 데이터 클래스"""

    host: str
    port: int
    client: redis.StrictRedis

    @classmethod
    def from_config(cls, node_config: dict) -> "RedisNode":
        """설정에서 RedisNode 인스턴스 생성"""
        host = node_config.get("host")
        port = node_config.get("port")

        if not host or not port:
            raise ValueError(f"잘못된 노드 설정: {node_config}")

        client = redis.StrictRedis(
            host=host, port=port, decode_responses=True, socket_timeout=5.0
        )
        return cls(host=host, port=port, client=client)


@dataclass
class RedisClusterManager:
    """Redis 클러스터 관리 데이터 클래스"""

    nodes: list[RedisNode]
    cluster_client: redis.RedisCluster
    node_map: dict[tuple[str, int], RedisNode]

    @classmethod
    def from_config(cls) -> "RedisClusterManager":
        """설정 파일에서 RedisClusterManager 인스턴스 생성"""
        if not config.get("redis_clusters"):
            raise ValueError("Redis 클러스터 설정이 없습니다.")

        try:
            # 노드 생성
            nodes: list[RedisNode] = [
                RedisNode.from_config(node) for node in config["redis_clusters"]
            ]

            # 클러스터 클라이언트 생성
            startup_nodes: list[ClusterNode] = [
                ClusterNode(host=node.host, port=node.port) for node in nodes
            ]
            cluster_client = redis.RedisCluster(
                startup_nodes=startup_nodes, decode_responses=True, socket_timeout=5.0
            )

            # 노드 맵 생성
            node_map: dict[tuple[str, int], RedisNode] = {
                (node.host, node.port): node for node in nodes
            }

            # 클러스터 연결 테스트
            cluster_client.ping()

            return cls(nodes=nodes, cluster_client=cluster_client, node_map=node_map)

        except redis.ConnectionError as e:
            logging.error(f"Redis 클러스터 연결 실패: {e}")
            raise ConnectionError(f"Redis 클러스터 연결 실패: {e}")
        except Exception as e:
            logging.error(f"Redis 클러스터 초기화 실패: {e}")
            raise

    def single_fetch_data(
        self, key: str, node_port: int | None = None
    ) -> str | dict | None:
        """
        데이터를 Redis 클러스터에서 조회
        Args:
            key (str): 조회할 키
            node_port (Optional[int]): 특정 노드의 포트 번호
        Returns:
            str | dict | None: 조회된 값
        """
        try:
            if node_port:
                # 포트로 노드 찾기
                node = next(
                    (node for node in self.nodes if node.port == node_port), None
                )
                if not node:
                    raise ValueError(
                        f"❌ 지정된 포트 {node_port}에 해당하는 노드가 없습니다."
                    )
                value = node.client.get(key)
            else:
                value = self.cluster_client.get(key)

            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None

        except Exception as e:
            logging.error(f"❌ 데이터 조회 실패 (키: {key}, 포트: {node_port}): {e}")
            print(f"❌ 데이터 조회 실패: {e}")
            return None
