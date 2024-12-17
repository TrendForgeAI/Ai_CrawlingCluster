"""
============================================================================================================ test session starts ============================================================================================================
platform darwin -- Python 3.12.7, pytest-8.3.4, pluggy-1.5.0
rootdir: /Users/imhaneul/Documents/project/TrendAI/Ai_CrawlingCluster
configfile: pyproject.toml
plugins: Faker-33.1.0, asyncio-0.25.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=function
collected 3 items                                                                                                                                                                                                                           

test_crawlers.py ...                                                                                                                                                                                                                  [100%]

============================================================================================================= 3 passed in 6.90s =============================================================================================================
"""

from common.types import UrlDictCollect
from configs.properties import (
    naver_id,
    naver_secret,
    naver_url,
    daum_auth,
    daum_url,
)
from crawlers.news_parsing import NaverDaumAsyncDataCrawling, GoogleAsyncDataReqestCrawling


class AsyncNaverNewsParsingDriver(NaverDaumAsyncDataCrawling):
    """네이버 NewsAPI 비동기 호출"""

    def __init__(self, target: str, count: int) -> None:
        """생성자 초기화"""
        self.header = {
            "X-Naver-Client-Id": naver_id,
            "X-Naver-Client-Secret": naver_secret,
        }
        self.url = f"{naver_url}/news.json?query={target}&start=1&display={count*10}"

        super().__init__(
            target, url=self.url, home="naver", count=count, header=self.header
        )

    async def news_collector(self) -> UrlDictCollect:
        data = await self.extract_news_urls(
            element="items", url_key="originallink", datetime_key="pubDate"
        )
        return data


class AsyncDaumNewsParsingDriver(NaverDaumAsyncDataCrawling):
    """다음 크롤링"""

    def __init__(self, target: str, count: int) -> None:
        """생성자 초기화"""
        self.header = {"Authorization": f"KakaoAK {daum_auth}"}
        self.url = f"{daum_url}?query={target} /news&page=1&size={count*10}"

        super().__init__(
            target, url=self.url, home="daum", count=count, header=self.header
        )

    async def news_collector(self) -> UrlDictCollect:
        data = await self.extract_news_urls(element="documents")
        return data


class AsyncGoogleNewsParsingDriver(GoogleAsyncDataReqestCrawling):
    """구글 크롤링"""

    def __init__(self, target: str, count: int) -> None:
        self.params = {
            "q": f"{target}",
            "tbm": "nws",
            "gl": "ko",
            "hl": "kr",
            "start": count * 10,
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.url = "https://www.google.com/search"
        super().__init__(
            target,
            url=self.url,
            home="google",
            count=count,
            param=self.params,
            header=None,
        )

    async def news_collector(self) -> UrlDictCollect:
        return await self.extract_news_urls()
