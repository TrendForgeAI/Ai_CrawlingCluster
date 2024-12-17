import asyncio
from typing import Callable

from crawlers.api_ndg import (
    AsyncDaumNewsParsingDriver,
    AsyncGoogleNewsParsingDriver,
    AsyncNaverNewsParsingDriver
)

# 크롤링 및 데이터 출력 함수 정의
async def crawl_and_insert(target: str, count: int, driver_class: Callable, source: str) -> None:
    driver = driver_class(target, count)
    data = await driver.news_collector()
    # 크롤링된 데이터를 출력
    print(f"{source}에서 {len(data)}개의 데이터를 크롤링했습니다.")

# fmt: off
async def crawling_data_insert_db(target: str, count: int) -> None:
    tasks = [
        # API 기반 크롤러 태스크
        crawl_and_insert(target, count, AsyncNaverNewsParsingDriver, "naver"),
        crawl_and_insert(target, count, AsyncDaumNewsParsingDriver, "daum"),
        crawl_and_insert(target, count, AsyncGoogleNewsParsingDriver, "google"),
    ]

    await asyncio.gather(*tasks)  # 모든 크롤링 작업을 동시에 수행

if __name__ == "__main__":
    asyncio.run(crawling_data_insert_db("BTC", 3))