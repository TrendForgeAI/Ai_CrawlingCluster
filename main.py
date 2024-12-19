import asyncio
from common.types import UrlDictCollect
from databases.cache.redis_cluster_manager import RedisClusterManager
from crawlers.api_ndg import (
    AsyncDaumNewsParsingDriver,
    AsyncNaverNewsParsingDriver,
)

API_CRAWLING = AsyncNaverNewsParsingDriver | AsyncDaumNewsParsingDriver


def redis_data_array() -> list[str]:
    """레디스에서 저장된 값 불러오기"""
    manager = RedisClusterManager()
    data: list[str] = manager.fetch_data("KR:question")
    return ["".join(pair) for pair in data][0]


# fmt: off
async def crawling_data(target: str, count: int) -> list[UrlDictCollect]:
    """API 파싱 본체"""
    async def crawl_and_insert(target: str, count: int, driver_class: API_CRAWLING) -> tuple[str, UrlDictCollect]:
        """크롤링 및 데이터 출력 함수 정의"""
        driver = driver_class(target, count)
        data: UrlDictCollect = await driver.news_collector()
        # 클래스명에서 'Async'와 'NewsParsingDriver' 제거하여 사이트명 추출
        site_name = driver_class.__name__.replace('Async', '').replace('NewsParsingDriver', '').lower()
        return site_name, data
    
    tasks = [
        crawl_and_insert(target, count, AsyncNaverNewsParsingDriver),
        crawl_and_insert(target, count, AsyncDaumNewsParsingDriver),
    ]
    results = await asyncio.gather(*tasks)
    return dict(results)


async def start():
    keyword = redis_data_array()
    return await crawling_data(keyword, 1)



if __name__ == "__main__":
    print(asyncio.run(start()))
