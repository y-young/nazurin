import abc
import os
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import AsyncContextManager, Generator, Optional, Union

import aiofiles
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from curl_cffi.requests import AsyncSession as CurlSession
from curl_cffi.requests import Response as CurlResponse

from nazurin.config import DOWNLOAD_CHUNK_SIZE, PROXY, TIMEOUT, UA
from nazurin.utils.logging import logger


class NazurinRequestSession(AbstractAsyncContextManager):
    def __init__(
        self,
        cookies: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: int = TIMEOUT,
        **kwargs
    ):
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, *args, **kwargs) -> AsyncContextManager:
        raise NotImplementedError

    @abc.abstractmethod
    async def download(self, url: str, destination: Union[str, os.PathLike]):
        raise NotImplementedError


class Request(ClientSession, NazurinRequestSession):
    """
    Wrapped ClientSession with default user agent,
    timeout and proxy support.
    """

    def __init__(
        self,
        cookies: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: int = TIMEOUT,
        **kwargs
    ):
        headers = headers or {}
        headers.update({"User-Agent": UA})
        timeout = ClientTimeout(total=timeout)

        connector = None
        if PROXY:
            connector = TCPConnector(ssl=False)
        super().__init__(
            connector=connector,
            cookies=cookies,
            headers=headers,
            trust_env=True,
            timeout=timeout,
            **kwargs
        )

    async def download(self, url: str, destination: Union[str, os.PathLike]):
        async with self.get(url) as response:
            if not response.ok:
                logger.error("Download failed with status code {}", response.status)
                logger.info("Response: {}", await response.content.read())
                response.raise_for_status()
            async with aiofiles.open(destination, "wb") as f:
                async for chunk in response.content.iter_chunked(DOWNLOAD_CHUNK_SIZE):
                    await f.write(chunk)


class CurlRequest(CurlSession, NazurinRequestSession):
    """
    Wrapped curl_cffi AsyncSession to impersonate a browser,
    with timeout and proxy support.
    """

    def __init__(
        self,
        cookies: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: int = TIMEOUT,
        **kwargs
    ):
        self.cookies = cookies
        self.headers = headers
        self.timeout = timeout
        self.proxies = {"https": PROXY, "http": PROXY} if PROXY else None
        super().__init__(**kwargs)

    @asynccontextmanager
    async def get(
        self, *args, impersonate: str = "chrome110", **kwargs
    ) -> Generator[CurlResponse, None, None]:
        yield await super().request(
            "GET",
            *args,
            cookies=self.cookies,
            headers=self.headers,
            timeout=self.timeout,
            impersonate=impersonate,
            proxies=self.proxies,
            **kwargs
        )

    async def download(self, url: str, destination: Union[str, os.PathLike]):
        async with self.get(url, stream=True) as response:
            if not response.ok:
                logger.error(
                    "Download failed with status code {}", response.status_code
                )
                logger.info("Response: {}", await response.acontent())
                response.raise_for_status()
            async with aiofiles.open(destination, "wb") as f:
                async for chunk in response.aiter_content():
                    await f.write(chunk)
