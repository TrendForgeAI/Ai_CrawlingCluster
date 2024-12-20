import logging
import aiohttp
import asyncio
import random
from dataclasses import dataclass, field
from common.logger import AsyncLogger
from common.types import (
    SelectHtmlOrJson,
    SelectHtml,
    SelectJson,
    SelectResponseType,
    UrlStatusCodeOrUrlAddress,
)
from common.abstract.abstract_async_request import (
    AbstractAsyncRequestAcquisition,
)



class AsyncRequestAcquisitionHTML(AbstractAsyncRequestAcquisition):
    """비동기 HTML 처리 클래스"""

    async def async_source(
        self, response: aiohttp.ClientResponse, response_type: str
    ) -> SelectHtmlOrJson:
        """
        비동기 HTML 또는 JSON 호출

        Args:
            response (aiohttp.ClientResponse) : session
            response_type (str): 가져올 데이터의 유형 ("html" 또는 "json")

        Returns:
            str | dict: HTML 또는 JSON 데이터
        """
        try:
            if response_type == "html":
                return await response.text()
            elif response_type == "json":
                return await response.json()
        except Exception as error:
            self.logging.log_message_sync(
                logging.ERROR, f"다음과 같은 에러로 가져올 수 없습니다 --> {error}"
            )

    async def async_request(
        self, response: aiohttp.ClientResponse
    ) -> UrlStatusCodeOrUrlAddress:
        """비동기 방식으로 원격 자원에 요청하고 상태 코드를 분류함

        Args:
            response (aiohttp.ClientResponse) : session

        Returns:
          UrlStatusCodeOrUrlAddress : 요청 결과 URL 또는 상태 코드
        """
        if response.status == 200:
            return self.url
        else:
            return {"status": response.status}

    async def async_type(
        self, type_: str, target: str, source: str | None = None
    ) -> SelectResponseType:
        """
        Args:
            type_ (str): html source 를 가지고 올지 url 상태를 가지고올지 선택
            target (str): 어디서 가지고 오는지 (주체)
            source (str | None, optional): html source를 가지고 올 format json or html 선택
        Returns:
            SelectResponseType: 선택한 함수 의 반환값
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.url, params=self.params, headers=self.headers
            ) as response:
                rs: int = random.randint(1, 5)
                await asyncio.sleep(rs)
                self.logging.log_message_sync(
                    logging.INFO,
                    message=f"""
                    {target}에서 다음과 같은 format을 사용했습니다 --> HTML,
                    시간 지연은 --> {rs}초 사용합니다,
                    """,
                )
                if type_ == "source":
                    return await self.async_source(response, source)
                elif type_ == "request":
                    return await self.async_request(response)


class AsyncRequestUrlStatus(AsyncRequestAcquisitionHTML):
    """URL Status(200이 아닐 경우) 또는 주소(200일 경우) 호출"""

    async def async_request_status(self) -> UrlStatusCodeOrUrlAddress:
        self.logging.log_message_sync(logging.INFO, f"URL statue를 요청했습니다")
        return await self.async_type(type_="request")


class AsyncRequestJSON(AsyncRequestAcquisitionHTML):
    """JSON 데이터 호출"""

    async def async_fetch_json(self, target: str) -> SelectJson:
        """URL에서 JSON 데이터를 비동기로 가져옴.

        Returns:
            SelectJson: JSON 데이터
        """
        self.logging.log_message_sync(
            logging.INFO, f"{target}에서 다음과 같은 format을 사용했습니다 --> JSON"
        )
        return await self.async_type(type_="source", source="json", target=target)


class AsyncRequestHTML(AsyncRequestAcquisitionHTML):
    """HTML 데이터 호출"""

    async def async_fetch_html(self, target: str) -> SelectHtml:
        """URL에서 HTML 데이터를 비동기로 가져옴.

        Returns:
            SelectHtml: HTML 데이터
        """

        return await self.async_type(type_="source", target=target, source="html")


@dataclass
class BasicAsyncNewsDataCrawling:
    target: str
    url: str
    home: str
    count: int | None = None
    header: dict[str, str] | None = None
    param: dict[str, str | int] | None = None
    _logging: callable = field(init=False, repr=False)

    def __post_init__(self):
        """API 요청하는 기본적으로 필요한 파라미터
        Args:
            target (str): 검색할 제시어
            url (str): 데이터를 가지고올 URL
            home (str): 페이지 주체 (google, naver, daum)
            count (int | None, optional): 얼마나 가지고 올껀지. 기본값 None.
            header (dict[str, str] | None, optional): 요청 헤더. 기본값 None.
            param (dict[str, str  |  int] | None, optional): get 파라미터. 기본값 None.
        """
        self._logging = AsyncLogger(
            target=self.home, log_file=f"{self.home}_crawling.log"
        ).log_message_sync
