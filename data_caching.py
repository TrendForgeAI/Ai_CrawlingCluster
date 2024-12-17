"""1회성 스크립트 이긴한데 재사용 가능성 있음"""

import yaml
import json
from typing import TypedDict, Required
from itertools import product
from databases.cache.redis_cluster_manager import RedisClusterManager
from databases.keyword import world_keywords, korea_keywords


class KeyWords(TypedDict):
    korea_combi: Required[list[set]]
    world_combi: Required[list[set]]
    mixin_combi: Required[list[set]]

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
def generate_combinations() -> KeyWords:
    """ 키워드 조합 데이터를 생성합니다.
    Returns:
        dict: 생성된 키워드 조합
    """
    return KeyWords(
        korea_combi=list(set(product(korea_keywords, korea_keywords))),
        world_combi=list(set(product(korea_keywords, korea_keywords))),
        mixin_combi=list(set(product(korea_keywords, korea_keywords))),
    )

# 데이터 저장 함수
def store_combinations(manager: RedisClusterManager, combinations: dict) -> None:
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
def cluster_main() -> None:
    """ Redis 클러스터에 데이터를 저장하는 메인 함수 """
    # 설정 로드 및 관리자 생성
    manager = RedisClusterManager()

    # 데이터 조합 생성 및 저장
    combinations = generate_combinations()
    store_combinations(manager, combinations)


if __name__ == "__main__":
    print("🔄 Redis Cluster 데이터 저장 시작...")
    cluster_main()
    print("✅ Redis Cluster 데이터 저장 완료.")