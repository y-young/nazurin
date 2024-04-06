import os
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import fromasctimeformat

from .config import DESTINATION, FILENAME


class Gelbooru:
    async def get_post(self, post_id: int):
        """Fetch an post."""
        api = (
            "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id="
            + str(post_id)
        )
        async with Request() as request, request.get(api) as response:
            response.raise_for_status()
            response_json = await response.json()
            if "post" not in response_json:
                raise NazurinError("Post not found")
            post = response_json["post"][0]
            return post

    async def fetch(self, post_id: int) -> Illust:
        post = await self.get_post(post_id)
        imgs = self.get_images(post)
        caption = self.build_caption(post)
        return Illust(int(post_id), imgs, caption, post)

    def get_images(self, post) -> List[Image]:
        """Get images from post."""
        url = post["file_url"]
        imgs = []
        destination, filename = self.get_storage_dest(post)
        imgs.append(
            Image(
                filename,
                url,
                destination,
                self.get_thumbnail(post),
                width=post["width"],
                height=post["height"],
            ),
        )
        return imgs

    @staticmethod
    def get_storage_dest(post: dict) -> Tuple[str, str]:
        """
        Format destination and filename.
        """

        created_at = fromasctimeformat(post["created_at"])
        filename, extension = os.path.splitext(post["image"])
        context = {
            **post,
            # Default filename (MD5), without extension
            "filename": filename,
            "created_at": created_at,
            "extension": extension,
        }
        filename = FILENAME.format_map(context)
        return (DESTINATION.format_map(context), filename + extension)

    @staticmethod
    def build_caption(post) -> Caption:
        tags = post["tags"].split(" ")
        tag_string = ""
        for tag in tags:
            tag_string += "#" + tag + " "
        return Caption(
            {
                "title": post["title"],
                "source": post["source"],
                "url": "https://gelbooru.com/index.php"
                f"?page=post&s=view&id={post['id']}",
                "tags": tag_string,
            },
        )

    @staticmethod
    def get_thumbnail(post) -> Optional[str]:
        """
        Get thumbnail URL from post['file_url'].
        eg:
        https://img3.gelbooru.com/images/a1/b2/12ab34cd56ef7890ab12cd34ef567890.jpg ->
        https://img3.gelbooru.com/samples/a1/b2/sample_12ab34cd56ef7890ab12cd34ef567890.jpg
        """

        if post["sample"] != 1:
            return None
        url = urlparse(post["file_url"])
        return (
            f"{url.scheme}://{url.netloc}/samples/"
            f"{post['directory']}/sample_{post['image']}"
        )
