from databases.keyword_generator import BaseCountry, load_countries_from_yaml
from databases.cache.redis_cluster_manager import RedisClusterManager
import logging

# 상수 정의
REDIS_EXPIRY_DAYS = 30
REDIS_EXPIRY_SECONDS = 60 * 60 * 24 * REDIS_EXPIRY_DAYS
KEYWORD_TYPES = ("core_keywords", "context_keywords")
logger = logging.getLogger(__name__)


class KeywordGenerator:
    def __init__(self, country_code: str) -> None:
        """KeywordGenerator 초기화"""
        self.country_code = country_code
        self.countries = load_countries_from_yaml()
        self.redis_manager = RedisClusterManager.from_config().cluster_client
        self.country = self.countries[country_code]
        self.base_key = country_code

    def _build_key(self, category: str, date: str | None = None) -> str:
        """Redis 키 생성 메서드"""
        key_type = f"crawled:{date}" if date else "default"
        return f"{self.base_key}:{key_type}:{category}"

    def _save_keywords(
        self, key: str, keywords: list[str], expire: bool = False
    ) -> None:
        """키워드 저장 유틸리티 메서드"""
        if not keywords:
            return

        self.redis_manager.sadd(key, *keywords)
        if expire:
            self.redis_manager.expire(key, REDIS_EXPIRY_SECONDS)
        logger.info(f"Saved {len(keywords)} keywords to Redis - Key: {key}")

    def save_redis_keywords(
        self,
        date: str | None = None,
        core_keywords: list[str] | None = None,
        context_keywords: list[str] | None = None,
    ) -> None:
        """Redis에 키워드 저장"""
        logger.info(
            f"Saving {'crawled' if date else 'default'} keywords for country: {self.country_code}"
        )

        for category, keywords in {
            "core_keywords": core_keywords or self.country.core_keywords,
            "context_keywords": context_keywords or self.country.context_keywords,
        }.items():
            self._save_keywords(
                self._build_key(category, date), keywords, expire=bool(date)
            )

    def _get_keywords_by_key(self, key: str) -> list[str]:
        """Redis 키로부터 키워드 가져오기"""
        return list(self.redis_manager.smembers(key))

    def get_keywords(self, date: str | None = None) -> tuple[list[str], list[str]]:
        """키워드 조회 (기본 또는 특정 날짜)"""
        keys: list[str] = [
            self._build_key(category, date) for category in KEYWORD_TYPES
        ]
        return tuple(self._get_keywords_by_key(key) for key in keys)

    def generate_templates_from_redis(
        self, date: str | None = None
    ) -> tuple[list[dict], dict]:
        """Redis에서 키워드를 가져와 템플릿 생성하고 각 템플릿별 사용된 키워드 정보 반환

        Returns:
            tuple[list[dict], dict]: (템플릿별 키워드 정보 리스트, 전체 키워드 정보)
        """
        # Redis 키 생성
        redis_keys = {
            category: self._build_key(category, date) for category in KEYWORD_TYPES
        }

        # 키워드 가져오기
        core_keywords, context_keywords = self.get_keywords(date)

        # 전체 키워드 정보 저장
        keywords_info = {
            "redis_keys": redis_keys,
            "core_keywords": core_keywords,
            "context_keywords": context_keywords,
        }

        temp_country = BaseCountry(
            name=self.country_code,
            core_keywords=core_keywords,
            context_keywords=context_keywords,
            templates=self.country.templates,
        )

        # 각 템플릿별 사용된 키워드 정보를 추적
        template_details = []
        search_queries = temp_country.generate_search_queries()
        templates = temp_country.apply_question_templates(search_queries)

        for template in templates:
            # 템플릿에서 사용된 키워드 찾기
            used_core = next((kw for kw in core_keywords if kw in template), "etc")
            used_context = next(
                (kw for kw in context_keywords if kw in template), "etc"
            )

            template_info = {
                "template": template,
                "core_keyword": used_core,
                "context_keyword": used_context,
            }
            template_details.append(template_info)

        return template_details, keywords_info


# KR:default:context_keywords
# 사용 예시
if __name__ == "__main__":
    generator = KeywordGenerator("KR")
    template_details, keywords_info = generator.generate_templates_from_redis()

    # 각 템플릿별 사용된 키워드 확인
    for detail in template_details:
        print(
            f"""
    템플릿: {detail['template']}
    사용된 core 키워드: {detail['core_keyword']}
    사용된 context 키워드: {detail['context_keyword']}
    -------------------"""
        )

    # 출력 예시:
    # 템플릿: GPT를 활용한 헬스케어 서비스의 장점은 무엇인가요?
    # 사용된 core 키워드: GPT
    # 사용된 context 키워드: 헬스케어
    # -------------------
