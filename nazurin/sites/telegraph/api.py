import hashlib
from http import HTTPStatus
from json import JSONDecodeError
from pathlib import PurePath
from urllib.parse import quote, unquote

from aiohttp import ContentTypeError

from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

from .config import DESTINATION
from .models import PATH_HASH_LENGTH, TelegraphIllust, build_archive_name

ASCII_CONTROL_END = 32
ASCII_DELETE = 127


def validate_page_path(value: str) -> str:
    """Validate and normalize a single-segment Telegraph page path."""
    page_path = unquote(value).strip("/")
    if (
        not page_path
        or page_path in {".", ".."}
        or "/" in page_path
        or "\\" in page_path
        or any(
            ord(char) < ASCII_CONTROL_END or ord(char) == ASCII_DELETE
            for char in page_path
        )
    ):
        raise NazurinError("Invalid Telegraph page path")
    return page_path


class Telegraph:
    API_BASE = "https://api.telegra.ph"

    @network_retry
    async def get_page(self, page_path: str) -> tuple[dict, dict]:
        """Fetch a Telegraph page and return the raw envelope and page data."""
        api_url = f"{self.API_BASE}/getPage/{quote(page_path, safe='')}"
        async with (
            Request() as request,
            request.get(
                api_url,
                params={"return_content": "true"},
            ) as response,
        ):
            if response.status == HTTPStatus.NOT_FOUND:
                raise NazurinError("Telegraph page not found")
            response.raise_for_status()
            try:
                envelope = await response.json()
            except (ContentTypeError, JSONDecodeError, ValueError) as error:
                raise NazurinError("Invalid Telegraph API response") from error

        if not isinstance(envelope, dict) or not isinstance(envelope.get("ok"), bool):
            raise NazurinError("Invalid Telegraph API response")
        if not envelope["ok"]:
            message = envelope.get("error") or "Unknown Telegraph API error"
            raise NazurinError(f"Telegraph API error: {message}")

        page = envelope.get("result")
        if not isinstance(page, dict):
            raise NazurinError("Invalid Telegraph API response")
        if not isinstance(page.get("path"), str):
            raise NazurinError("Invalid Telegraph API response")
        if not isinstance(page.get("title"), str) or not page["title"]:
            raise NazurinError("Invalid Telegraph API response")
        if not isinstance(page.get("content"), list):
            raise NazurinError("Invalid Telegraph API response")

        page = {**page, "path": validate_page_path(page["path"])}
        return envelope, page

    async def fetch(self, page_path: str, source_url: str) -> TelegraphIllust:
        envelope, page = await self.get_page(page_path)
        destination = self.get_storage_destination(page)
        return TelegraphIllust(envelope, page, source_url, destination)

    @staticmethod
    def get_storage_destination(page: dict) -> str:
        values = {
            **page,
            "archive_name": build_archive_name(page),
            "path_hash": hashlib.sha256(page["path"].encode()).hexdigest()[
                :PATH_HASH_LENGTH
            ],
        }
        try:
            destination = DESTINATION.format_map(values)
        except (KeyError, ValueError) as error:
            raise NazurinError("Invalid Telegraph file path template") from error

        parsed = PurePath(destination)
        if parsed.is_absolute() or not parsed.parts or ".." in parsed.parts:
            raise NazurinError("Invalid Telegraph file destination")
        return destination
