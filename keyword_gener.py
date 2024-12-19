import json
from databases.keyword_generator import BaseCountry, load_countries_from_yaml
from databases.cache.redis_cluster_manager import RedisClusterManager


def generate_korea_questions(country_code: str) -> set[str]:
    """
    한국에 대한 질문을 생성하고 반환하는 메인 함수
    Returns:
        한국 관련 생성된 질문 리스트
    """
    countries: dict[str, BaseCountry] = load_countries_from_yaml()
    country: BaseCountry = countries[country_code]
    return country.apply_question_templates(country.generate_search_queries())


def save_redis_keyword(country_code: str) -> None:
    """레디스 저장

    Args:
        country_code (str): 국가 코드
    """
    c: list[str] = list(generate_korea_questions(country_code))
    manager = RedisClusterManager()
    manager.store_data("KR:question", value=json.dumps(c))


save_redis_keyword("KR")
