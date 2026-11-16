from dataclasses import dataclass
from http import HTTPStatus

from aiohttp import ClientResponseError
from multidict import CIMultiDict

from nazurin.models import Illust
from nazurin.utils.exceptions import NazurinError

from .config import UA, USER_ID_HINT


@dataclass
class DanbooruIllust(Illust):
    async def download(self, **kwargs):
        headers = CIMultiDict(kwargs.pop("headers", None) or {})
        headers["User-Agent"] = UA
        try:
            await super().download(headers=headers, **kwargs)
        except ClientResponseError as err:
            if err.status != HTTPStatus.FORBIDDEN:
                raise
            raise NazurinError(
                f"Failed to download file: {err}\n{USER_ID_HINT}",
            ) from err
