import asyncio
from databases.cache.redis_cluster_manager import RedisClusterManager
from typing import Callable

from crawlers.api_ndg import (
    AsyncDaumNewsParsingDriver,
    # AsyncGoogleNewsParsingDriver,
    AsyncNaverNewsParsingDriver
)

def redis_data_array() -> list[str]:
    manager = RedisClusterManager()
    data: list[list[str]] = manager.fetch_data("node7002:mixin_combination")
    return [" ".join(pair) for pair in data]

# # 크롤링 및 데이터 출력 함수 정의
async def crawl_and_insert(target: str, count: int, driver_class: Callable) -> None:
    driver = driver_class(target, count)
    data = await driver.news_collector()
    return data

# fmt: off
async def crawling_data_insert_db(target: str, count: int) -> None:
    tasks: list[list[dict[str, str]]] = [
        # API 기반 크롤러 태스크
        crawl_and_insert(target, count, AsyncNaverNewsParsingDriver),
        crawl_and_insert(target, count, AsyncDaumNewsParsingDriver),
    ]
    return await asyncio.gather(*tasks)

    
async def crawling_keyword() -> None:
    """레디스에서 가지고온 값"""
    tasks = [crawling_data_insert_db(target, 1) for target in redis_data_array()]
    return await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(crawling_keyword())