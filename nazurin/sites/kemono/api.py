import os
from datetime import datetime, timezone
from mimetypes import guess_type
from typing import Tuple

from bs4 import BeautifulSoup

from nazurin.models import Caption, Illust, Image
from nazurin.models.file import File
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

from .config import DESTINATION, FILENAME


class Kemono:
    @network_retry
    async def get_post(self, service: str, user_id: str, post_id: str) -> dict:
        """Fetch an post."""
        api = f"https://kemono.su/api/v1/{service}/user/{user_id}/post/{post_id}"
        async with Request() as request:
            async with request.get(api) as response:
                response.raise_for_status()
                post = await response.json()
                if not post:
                    raise NazurinError("Post not found")
                username = await self.get_username(service, user_id)
                post["username"] = username
                return post

    @network_retry
    async def get_username(self, service: str, user_id: str) -> str:
        url = f"https://kemono.su/{service}/user/{user_id}"
        async with Request() as request:
            async with request.get(url) as response:
                response.raise_for_status()
                response = await response.text()
                soup = BeautifulSoup(response, "html.parser")
                tag = soup.find("meta", attrs={"name": "artist_name"})
                if not tag:
                    return ""
                username = tag.get("content", "")
                return username

    async def fetch(self, service: str, user_id: str, post_id: str) -> Illust:
        post = await self.get_post(service, user_id, post_id)
        caption = self.build_caption(post)

        images = []
        download_files = []
        files = [post["file"]] if post.get("file") else []
        files += post["attachments"]
        if not files:
            raise NazurinError("No files found")

        for file in files:
            path: str = file["path"]

            # Handle non-image files
            url = "https://c1.kemono.party/data" + path
            destination, filename = self.get_storage_dest(post, file["name"], path)
            if not self.is_image(path):
                if post["service"] == "dlsite" and path.endswith(".html"):
                    # HTML files from DLSite seems useless
                    continue
                download_files.append(File(filename, url, destination))
                continue

            # Handle images
            thumbnail = "https://img.kemono.party/thumbnail/data" + path
            images.append(
                Image(
                    filename,
                    url,
                    destination,
                    thumbnail,
                )
            )

        return Illust(images, caption, post, download_files)

    @staticmethod
    def get_storage_dest(post: dict, pretty_name: str, path: str) -> Tuple[str, str]:
        """
        Format destination and filename.
        """

        def parse_time(time: str) -> str:
            return datetime.fromisoformat(time).replace(tzinfo=timezone.utc)

        added = parse_time(post["added"])
        edited = parse_time(post["edited"] or post["added"])
        published = parse_time(post["published"])
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
    def build_caption(post) -> Caption:
        return Caption(
            {
                "title": post["title"],
                "author": "#" + post["username"],
                "url": (
                    f"https://kemono.party/{post['service']}"
                    f"/user/{post['user']}/post/{post['id']}"
                ),
            }
        )

    @staticmethod
    def is_image(path: str) -> bool:
        """Check if path is an image by mimetype."""
        mimetype = guess_type(path)[0]
        return mimetype and mimetype.startswith("image")
