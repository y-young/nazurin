import os
from datetime import datetime, timezone
from http import HTTPStatus
from mimetypes import guess_type
from typing import Any, ClassVar, TypeVar
from urllib.parse import quote

from nazurin.models import Caption, Illust, Image
from nazurin.models.file import File
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import fromisoformat

from .config import DESTINATION, FILENAME

T = TypeVar("T")


class KemonoRequest:
    """Custom request class for Kemono API with built-in headers and JSON handling."""

    API_BASE: ClassVar[str] = "https://kemono.cr/api/v1"
    HEADERS: ClassVar[dict[str, str]] = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/145.0.0.0 Safari/537.36"
        ),
        "Referer": "https://kemono.cr/",
        "Accept": "text/css",
        "Accept-Language": "en-US;q=1.0",
    }

    async def get(
        self,
        path: str,
        response_type: type[T],
    ) -> T:
        """Make a GET request and return the decoded JSON response.

        Args:
            path: Relative path appended to the API base URL.
            response_type: Expected response type for generic type inference.
        """
        url = f"{self.API_BASE}/{path}"
        async with (
            Request() as session,
            session.get(url, headers=self.HEADERS) as response,
        ):
            if response.status == HTTPStatus.FORBIDDEN:
                content = await response.text()
                raise NazurinError(f"403 Forbidden: {content[:100]}")
            response.raise_for_status()
            return await response.json(content_type=None)


class Kemono:
    _client: ClassVar[KemonoRequest] = KemonoRequest()

    @network_retry
    async def get_post(self, service: str, user_id: str, post_id: str) -> dict:
        """Fetch a post."""
        api = f"{service}/user/{user_id}/post/{post_id}"
        data = await self._client.get(api, dict[str, Any])
        post = data.get("post", data)
        username = await self.get_username(service, user_id)
        post["username"] = username
        return post

    @network_retry
    async def get_post_revision(
        self,
        service: str,
        user_id: str,
        post_id: str,
        revision_id: str,
    ) -> dict:
        """Fetch a post revision."""
        api = f"{service}/user/{user_id}/post/{post_id}/revisions"
        revisions = await self._client.get(api, list[dict[str, Any]])
        post = None
        for revision in revisions:
            if str(revision["revision_id"]) == revision_id:
                post = revision
                break
        if not post:
            raise NazurinError("Post revision not found")
        username = await self.get_username(service, user_id)
        post["username"] = username
        return post

    @network_retry
    async def get_username(self, service: str, user_id: str) -> str:
        path = f"{service}/user/{user_id}/profile"
        profile = await self._client.get(path, dict[str, Any])
        if isinstance(profile, list) and len(profile) > 0:
            return profile[0].get("name", "")
        return profile.get("name", "")

    async def fetch(
        self,
        service: str,
        user_id: str,
        post_id: str,
        revision_id: str | None,
    ) -> Illust:
        if revision_id:
            post = await self.get_post_revision(service, user_id, post_id, revision_id)
        else:
            post = await self.get_post(service, user_id, post_id)
        caption = self.build_caption(post)

        images: list[Image] = []
        download_files: list[File] = []
        files: list[dict[str, Any]] = [post["file"]] if post.get("file") else []
        files += post.get("attachments", [])

        if not files:
            raise NazurinError("No files found")

        image_index = 0
        for file in files:
            path: str = file["path"]
            file_name_param = file.get("name", "")

            encoded_filename = quote(file_name_param)
            url = f"https://n2.kemono.cr/data{path}?f={encoded_filename}"

            # Handle non-image files
            if not self.is_image(path):
                if post["service"] == "dlsite" and path.endswith(".html"):
                    # HTML files from DLSite seems useless
                    continue
                destination, filename = self.get_storage_dest(post, file["name"], path)
                download_files.append(File(filename, url, destination))
                continue

            # Handle images
            destination, filename = self.get_storage_dest(
                post,
                f"{image_index} - {file['name']}",
                path,
            )

            thumbnail = f"https://img.kemono.cr/thumbnail/data{path}"

            images.append(
                Image(
                    filename,
                    url,
                    destination,
                    thumbnail,
                ),
            )
            image_index += 1

        identifier = filter(lambda x: x, [service, user_id, post_id, revision_id])
        return Illust("_".join(identifier), images, caption, post, download_files)

    @staticmethod
    def get_storage_dest(post: dict, pretty_name: str, path: str) -> tuple[str, str]:
        """
        Format destination and filename.
        """

        def parse_time(time_str: Any) -> datetime:
            default_time = datetime(1970, 1, 1, tzinfo=timezone.utc)
            if not time_str or not isinstance(time_str, str):
                return default_time
            try:
                return fromisoformat(time_str).replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                return default_time

        added = parse_time(post.get("added"))
        edited = parse_time(post.get("edited") or post.get("added"))
        published = parse_time(post.get("published") or post.get("added"))
        pretty_name, _ = os.path.splitext(pretty_name)
        filename, extension = os.path.splitext(path)
        context = {
            **post,
            # Default filename provided by Kemono, without extension
            "filename": filename,
            # Filename provided by author, with extension
            "pretty_name": pretty_name,
            "added": added,
            "edited": edited,
            "published": published,
            "extension": extension,
        }
        filename = FILENAME.format_map(context)
        return (DESTINATION.format_map(context), filename + extension)

    @staticmethod
    def get_url(post: dict) -> str:
        url = (
            f"https://kemono.cr/{post['service']}/user/{post['user']}/post/{post['id']}"
        )
        revision = post.get("revision_id")
        if revision:
            url += f"/revision/{post['revision_id']}"
        return url

    @staticmethod
    def build_caption(post: dict[str, Any]) -> Caption:
        return Caption(
            {
                "title": post["title"],
                "author": "#" + post["username"],
                "url": Kemono.get_url(post),
            },
        )

    @staticmethod
    def is_image(path: str) -> bool:
        """Check if path is an image by mimetype."""
        mimetype = guess_type(path)[0]
        return mimetype is not None and mimetype.startswith("image")
