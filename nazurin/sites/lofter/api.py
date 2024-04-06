import json
import os
from datetime import datetime, timezone
from http import HTTPStatus
from typing import List, Tuple
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

from .config import DESTINATION, FILENAME


class Lofter:
    API = "https://api.lofter.com/oldapi/post/detail.api"
    UA = "LOFTER/6.24.0 (iPhone; iOS 15.4.1; Scale/3.00)"

    @network_retry
    async def get_post(self, username: str, permalink: str) -> dict:
        """Fetch a post."""
        (blog_id, post_id) = await self.get_real_id(username, permalink)
        async with Request(headers={"User-Agent": self.UA}) as request, request.post(
            self.API,
            data={
                "targetblogid": blog_id,
                "postid": post_id,
            },
        ) as response:
            response.raise_for_status()

            data = await response.json()
            if data["meta"]["status"] != HTTPStatus.OK:
                raise NazurinError(data["meta"]["msg"])

            post = data["response"]["posts"][0]["post"]
            return post

    async def fetch(self, username: str, permalink: str) -> Illust:
        post = await self.get_post(username, permalink)
        imgs = self.get_images(post)
        caption = Caption(
            {
                "author": post["blogInfo"]["blogNickName"]
                + " #"
                + post["blogInfo"]["blogName"],
                "url": post["blogPageUrl"],
                "tags": " ".join(["#" + tag for tag in post["tagList"]]),
            },
        )
        return Illust(int(post["id"]), imgs, caption, post)

    @staticmethod
    def get_images(post: dict) -> List[Image]:
        """Get images from post."""
        if "photoLinks" not in post:
            raise NazurinError("No images found")

        photos = json.loads(post["photoLinks"])
        imgs = []
        for index, photo in enumerate(photos):
            url = photo["raw"]
            filename = os.path.basename(url)
            destination, filename = Lofter.get_storage_dest(post, filename, index)
            imgs.append(
                Image(
                    filename,
                    url,
                    destination,
                    thumbnail=photo["orign"],
                    width=photo["rw"],
                    height=photo["rh"],
                ),
            )
        return imgs

    @staticmethod
    def get_storage_dest(post: dict, filename: str, index: int) -> Tuple[str, str]:
        """
        Format destination and filename.
        """

        publish_time = datetime.fromtimestamp(
            post["publishTime"] / 1000,
            tz=timezone.utc,
        )
        filename, extension = os.path.splitext(filename)
        context = {
            **post,
            # Default filename, without extension
            "filename": filename,
            "publishTime": publish_time,
            "extension": extension,
            "index": index,
            "blogName": post["blogInfo"]["blogName"],
            "nickName": post["blogInfo"]["blogNickName"],
        }
        filename = FILENAME.format_map(context)
        return (DESTINATION.format_map(context), filename + extension)

    @network_retry
    async def get_real_id(self, username: str, post_id: str) -> Tuple[int, int]:
        """Get real numeric blog ID and post ID."""
        api = f"https://{username}.lofter.com/post/{post_id}"
        async with Request() as request, request.get(api) as response:
            if response.status == HTTPStatus.NOT_FOUND:
                raise NazurinError("Post not found")
            response.raise_for_status()

            response_text = await response.text()
            soup = BeautifulSoup(response_text, "html.parser")
            iframe = soup.find("iframe", id="control_frame")
            if not iframe:
                raise NazurinError("Failed to get real post ID")
            src = urlparse(iframe.get("src"))
            query = parse_qs(src.query)
            return (query["blogId"][0], query["postId"][0])
