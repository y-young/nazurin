import os
from datetime import datetime
from http import HTTPStatus
from typing import List, Tuple

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

from .config import DESTINATION, FILENAME


class Artstation:
    @network_retry
    async def get_post(self, post_id: str):
        """Fetch a post."""
        api = f"https://www.artstation.com/projects/{post_id}.json"
        async with Request() as request, request.get(api) as response:
            if response.status == HTTPStatus.NOT_FOUND:
                raise NazurinError("Post not found")
            response.raise_for_status()
            post = await response.json()
            return post

    async def fetch(self, post_id: str) -> Illust:
        post = await self.get_post(post_id)
        imgs = self.get_images(post)
        caption = self.build_caption(post)
        return Illust(post_id, imgs, caption, post)

    def get_images(self, post) -> List[Image]:
        """Get images from post."""
        if "assets" not in post:
            raise NazurinError("No asset found.")
        assets = sorted(post["assets"], key=lambda x: x["position"])
        imgs = []
        index = 0
        for asset in assets:
            if asset["asset_type"] != "image":
                continue
            # https://cdnb.artstation.com/p/assets/images/images/042/908/363/large/_z-ed_-da.jpg?1635784439
            _, url, thumbnail = self.parse_url(asset["image_url"])
            destination, filename = self.get_storage_dest(post, asset, index)
            imgs.append(
                Image(
                    filename,
                    url,
                    destination,
                    thumbnail,
                    width=asset["width"],
                    height=asset["height"],
                ),
            )
            index += 1
        return imgs

    @staticmethod
    def get_storage_dest(post: dict, asset: dict, index: int = 0) -> Tuple[str, str]:
        """
        Format destination and filename.
        """

        # https://cdnb.artstation.com/p/assets/images/images/042/908/363/large/_z-ed_-da.jpg?1635784439
        filename = Artstation.parse_url(asset["image_url"])[0]
        filename, ext = os.path.splitext(filename)
        context = {
            **post,
            "created_at": datetime.fromisoformat(post["created_at"]),
            "updated_at": datetime.fromisoformat(post["updated_at"]),
            "asset": asset,
            "filename": filename,
            "extension": ext,
            "index": index,
        }
        return (DESTINATION.format_map(context), FILENAME.format_map(context) + ext)

    @staticmethod
    def build_caption(post) -> Caption:
        user = post["user"]
        tags = post["tags"]
        tag_string = ""
        for tag in tags:
            tag_string += "#" + tag + " "
        return Caption(
            {
                "title": post["title"],
                "author": f"{user['full_name']} #{user['username']}",
                "url": f"https://www.artstation.com/artwork/{post['hash_id']}",
                "tags": tag_string,
            },
        )

    @staticmethod
    def parse_url(src: str) -> Tuple[str, str, str]:
        """Get filename, original file url & thumbnail url of the original image

        eg:
        - src:
            'https://cdnb.artstation.com/p/assets/images/images/042/908/363/large/_z-ed_-da.jpg'

        - return:
            '_z-ed_-da.jpg',
            'https://cdnb.artstation.com/p/assets/images/images/042/908/363/4k/_z-ed_-da.jpg',
            'https://cdnb.artstation.com/p/assets/images/images/042/908/363/medium/_z-ed_-da.jpg'

        """
        baseurl = src.split("?")[0]
        basename = os.path.basename(baseurl)
        url = baseurl.replace("/large/", "/4k/")
        thumbnail = baseurl.replace("/large/", "/medium/")
        return basename, url, thumbnail
