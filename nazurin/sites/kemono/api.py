import os
from datetime import datetime, timezone
from mimetypes import guess_type
from typing import ClassVar
from urllib.parse import quote

from nazurin.models import Caption, Illust, Image
from nazurin.models.file import File
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

from .config import DESTINATION, FILENAME


class Kemono:
    API_BASE: ClassVar[str] = "https://kemono.cr/api/v1"

    HEADERS: ClassVar[dict] = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/145.0.0.0 Safari/537.36"
        ),
        "Referer": "https://kemono.cr/",
        "Accept": "text/css",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6",
    }

    @network_retry
    async def get_post(self, service: str, user_id: str, post_id: str) -> dict:
        """Fetch a post."""
        api = f"{self.API_BASE}/{service}/user/{user_id}/post/{post_id}"
        async with (
            Request() as request,
            request.get(api, headers=self.HEADERS) as response,
        ):
            if response.status == 403:  # noqa: PLR2004
                content = await response.text()
                raise NazurinError(f"403 Forbidden: {content[:100]}")

            response.raise_for_status()

            data = await response.json(content_type=None)

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
        api = f"{self.API_BASE}/{service}/user/{user_id}/post/{post_id}/revisions"
        async with (
            Request() as request,
            request.get(api, headers=self.HEADERS) as response,
        ):
            response.raise_for_status()
            revisions = await response.json(content_type=None)
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
        url = f"{self.API_BASE}/{service}/user/{user_id}/profile"
        async with (
            Request() as request,
            request.get(url, headers=self.HEADERS) as response,
        ):
            response.raise_for_status()
            profile = await response.json(content_type=None)
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

        images = []
        download_files = []
        files = [post["file"]] if post.get("file") else []
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

        def parse_time(time_str):
            # Define default time (1970-01-01)
            if not time_str or not isinstance(time_str, str):
                return datetime(1970, 1, 1, tzinfo=timezone.utc)
            try:
                return datetime.fromisoformat(time_str.replace("Z", "+00:00")).replace(
                    tzinfo=timezone.utc
                )
            except (ValueError, TypeError):
                return datetime(1970, 1, 1, tzinfo=timezone.utc)

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
            f"https://kemono.su/{post['service']}/user/{post['user']}/post/{post['id']}"
        )
        revision = post.get("revision_id")
        if revision:
            url += f"/revision/{post['revision_id']}"
        return url

    @staticmethod
    def build_caption(post) -> Caption:
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
        return mimetype and mimetype.startswith("image")
