import json
import os
import re
from datetime import datetime, timezone
from http import HTTPStatus
from typing import List, Tuple

from bs4 import BeautifulSoup

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

from .config import DESTINATION, FILENAME


class Lofter:
    API = "https://api.lofter.com/oldapi/post/detail.api"
    UA = "LOFTER/8.1.12 (iPhone; iOS 18.3.1; Scale/3.00)"

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
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "sec-fetch-site": "none",
            "accept-encoding": "gzip, deflate, br",
            "sec-fetch-mode": "navigate",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/135 Mobile/15E148 Version/15.0",
            "accept-language": "en-US,en;q=0.9",
            "sec-fetch-dest": "document"
        }

        async with Request(headers=headers) as request, request.get(api) as response:
            if response.status == HTTPStatus.NOT_FOUND:
                raise NazurinError("Post not found")
            response.raise_for_status()

            response_text = await response.text()
            soup = BeautifulSoup(response_text, "html.parser")
            script_tag = soup.find('script', text=re.compile('window.__initialize_data__'))
            if not script_tag:
                raise NazurinError("Failed to get real post ID")
            script_content = script_tag.string
            match = re.search(r'window\.__initialize_data__\s*=\s*({.*});?', script_content, re.DOTALL)
            if not match:
                raise NazurinError("Failed to get real post ID")
            json_str = match.group(1)
            data = json.loads(json_str)
            # 根据数据层级获取 id 和 blogId
            post_view = data['postData']['data']['postData']['postView']
            post_id = post_view['id']
            blog_id = post_view['blogId']
            return (blog_id, post_id)
