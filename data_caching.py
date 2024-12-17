import yaml
import json
from pathlib import Path
from itertools import product
from databases.cache.redis_cluster_manager import RedisClusterManager
from databases.keyword_redis import world_keywords, korea_keywords


# YAML 설정 로드
def load_config(file_path: str) -> dict:
    """ YAML 설정 파일을 불러옵니다.
    Args:
        file_path (str): 설정 파일 경로
    Returns:
        dict: 설정 데이터
    """
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


# 데이터 조합 생성
def generate_combinations() -> dict:
    """ 키워드 조합 데이터를 생성합니다.
    Returns:
        dict: 생성된 키워드 조합
    """
    return {
        "korea_combi": list(set(product(korea_keywords, korea_keywords))),
        "world_combi": list(set(product(world_keywords, world_keywords))),
        "mixin_combi": list(set(product(korea_keywords, world_keywords))),
    }


# 데이터 저장 함수
def store_combinations(manager: RedisClusterManager, combinations: dict):
    """ Redis 클러스터에 조합 데이터를 저장합니다.
    Args:
        manager (RedisClusterManager): Redis 클러스터 관리자 인스턴스
        combinations (dict): 저장할 키워드 조합 데이터
    """
    # Redis에 데이터 저장
    data_to_store = [
        ("node7000:korea_keywords", korea_keywords),
        ("node7000:global_keywords", world_keywords),
        ("node7001:korea_combination", combinations["korea_combi"][:len(combinations["korea_combi"]) // 2]),
        ("node7002:global_combination", combinations["world_combi"][len(combinations["world_combi"]) // 2:]),
        ("node7002:mixin_combination", combinations["mixin_combi"][len(combinations["mixin_combi"]) // 2:]),
    ]

    for key, value in data_to_store:
        manager.store_data(key, json.dumps(value))
        print(f"✅ '{key}' 데이터 저장 완료.")


# 메인 실행 함수
def cluster_main():
    """ Redis 클러스터에 데이터를 저장하는 메인 함수 """
    # 설정 로드 및 관리자 생성
    cluster_location = Path(__file__).parent
    config = load_config(f"{cluster_location}/configs/cy/database.yaml")
    manager = RedisClusterManager()

    # 데이터 조합 생성 및 저장
    combinations = generate_combinations()
    store_combinations(manager, combinations)


if __name__ == "__main__":
    print("🔄 Redis Cluster 데이터 저장 시작...")
    cluster_main()
    print("✅ Redis Cluster 데이터 저장 완료.")