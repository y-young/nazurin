from __future__ import annotations

from http import HTTPStatus
from json import JSONDecodeError
from pathlib import PurePath

from aiohttp import ContentTypeError
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

from .config import DESTINATION
from .models import TelegraphIllust, build_archive_name, build_path_hash


class TelegraphModel(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)


class TelegraphNodeElement(TelegraphModel):
    tag: str
    attrs: dict[str, str] | None = None
    children: list[str | TelegraphNodeElement] | None = None


class TelegraphPage(TelegraphModel):
    path: str
    url: str
    title: str = Field(min_length=1)
    description: str
    author_name: str | None = None
    author_url: str | None = None
    image_url: str | None = None
    content: list[str | TelegraphNodeElement]
    views: int
    can_edit: bool | None = None


class TelegraphResponse(TelegraphModel):
    ok: bool
    result: TelegraphPage | None = None
    error: str | None = None


class Telegraph:
    API_BASE = "https://api.telegra.ph"

    @network_retry
    async def get_page(self, page_path: str) -> tuple[dict, dict]:
        """Fetch a Telegraph page and return the raw envelope and page data."""
        api_url = f"{self.API_BASE}/getPage/{page_path}"
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

        try:
            api_response = TelegraphResponse.model_validate(envelope)
        except ValidationError as error:
            raise NazurinError("Invalid Telegraph API response") from error
        if not api_response.ok:
            message = api_response.error or "Unknown Telegraph API error"
            raise NazurinError(f"Telegraph API error: {message}")

        if api_response.result is None:
            raise NazurinError("Invalid Telegraph API response")
        page = api_response.result.model_dump(exclude_unset=True)
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
            "path_hash": build_path_hash(page["path"]),
        }
        try:
            destination = DESTINATION.format_map(values)
        except (KeyError, ValueError) as error:
            raise NazurinError("Invalid Telegraph file path template") from error

        parsed = PurePath(destination)
        if parsed.is_absolute() or not parsed.parts or ".." in parsed.parts:
            raise NazurinError("Invalid Telegraph file destination")
        return destination
