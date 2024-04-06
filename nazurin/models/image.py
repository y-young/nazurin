import os
from dataclasses import dataclass
from typing import Optional

import aiohttp
from humanize import naturalsize

from nazurin.utils import Request, logger
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import check_image

from .file import File

TG_IMG_WIDTH_HEIGHT_RATIO_LIMIT = 20
TG_IMG_DIMENSION_LIMIT = 10000

INVALID_IMAGE_RETRIES = 3


@dataclass
class Image(File):
    thumbnail: str = None
    _size: Optional[int] = None
    """
    File size in bytes
    """
    width: int = 0
    height: int = 0
    _chosen_url: str = None

    async def display_url(self) -> str:
        return await self.chosen_url()

    async def chosen_url(self) -> str:
        # Conform with limitations of sending photos:
        # https://core.telegram.org/bots/api#sendphoto
        if self._chosen_url:
            return self._chosen_url

        if (
            self.height != 0
            and self.width / self.height > TG_IMG_WIDTH_HEIGHT_RATIO_LIMIT
        ):
            raise NazurinError(
                "Width and height ratio of image exceeds 20, try download option.",
            )
        self._chosen_url = self.url
        if self.thumbnail:
            # For safety reasons, use thumbnail when image size is unknown
            if (
                (not self.width)
                or (not self.height)
                or self.width + self.height > TG_IMG_DIMENSION_LIMIT
            ):
                self._chosen_url = self.thumbnail
                logger.info(
                    "Use thumbnail (Unkown image size or width + height > 10000 "
                    "[{width}, {height}]): {url}",
                    width=self.width,
                    height=self.height,
                    url=self._chosen_url,
                )
            else:
                size = await self.size()
                if (not size) or size > 5 * 1024 * 1024:
                    self._chosen_url = self.thumbnail
                    logger.info(
                        "Use thumbnail (Unknown size or size > 5MB [{}]): {}",
                        size,
                        self._chosen_url,
                    )
        return self._chosen_url

    async def size(self, **kwargs) -> int:
        self._size = self._size or await super().size()
        if self._size:
            return self._size
        async with Request(**kwargs) as request, request.head(self.url) as response:
            headers = response.headers
            if "Content-Length" in headers:
                self._size = int(headers["Content-Length"])
                logger.info(
                    "Got image size: {}",
                    naturalsize(self._size, binary=True),
                )
            else:
                logger.info("Failed to get image size")
            return self._size

    def __post_init__(self):
        if self._size:
            self.set_size(self._size)
        return super().__post_init__()

    def set_size(self, value: int):
        if value % 1 != 0:
            raise TypeError("Image size must be an integer")
        self._size = int(value)

    async def download(self, session: aiohttp.ClientSession):
        for i in range(INVALID_IMAGE_RETRIES):
            downloaded_size = await super().download(session)
            is_valid = await check_image(self.path)
            attempt_count = f"{i + 1} / {INVALID_IMAGE_RETRIES}"
            if is_valid:
                if self._size is None or self._size == downloaded_size:
                    return
                logger.warning(
                    "Downloaded file size {} does not match image size {}, attempt {}",
                    downloaded_size,
                    self._size,
                    attempt_count,
                )
            else:
                logger.warning(
                    "Downloaded image {} is not valid, attempt {}",
                    self.path,
                    attempt_count,
                )
            if i < INVALID_IMAGE_RETRIES - 1:
                # Keep the last one for debugging
                os.remove(self.path)
        raise NazurinError(
            "Download failed with invalid image, please check logs for details",
        )
