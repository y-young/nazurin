import json
import os
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from urllib.parse import unquote

from aiohttp.client_exceptions import ClientResponseError
from bs4 import BeautifulSoup
from pybooru import Moebooru as MoebooruBase

from nazurin.config import TEMP_DIR
from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request, logger
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import ensure_existence_async, snake_to_pascal

from .config import COLLECTIONS, DESTINATION, FILENAME


class Moebooru:
    def __init__(self):
        self.url = "yande.re"

    def site(self, site_url: Optional[str] = "yande.re"):
        self.url = site_url
        return self

    @network_retry
    async def get_post(self, post_id: int):
        url = "https://" + self.url + "/post/show/" + str(post_id)
        async with Request() as request, request.get(url) as response:
            try:
                response.raise_for_status()
            except ClientResponseError as err:
                raise NazurinError(err) from None
            response_text = await response.text()
        soup = BeautifulSoup(response_text, "html.parser")
        tag = soup.find(id="post-view").find(recursive=False)
        if tag.name == "script":
            content = str.strip(tag.string)
        elif tag.name == "div" and ("status-notice" in tag["class"]):
            raise NazurinError(tag.get_text(strip=True))
        else:
            logger.error(tag)
            raise NazurinError("Unknown error")

        info = content[19:-2]
        try:
            info = json.loads(info)
            post = info["posts"][0]
            tags = info["tags"]
        except json.decoder.JSONDecodeError:
            logger.exception("Failed to decode JSON")
        return post, tags

    async def view(self, post_id: int) -> Illust:
        post, tags = await self.get_post(post_id)
        imgs = self.get_images(post)
        caption = self.build_caption(post, tags)
        return Illust(post_id, imgs, caption, post)

    def pool(self, pool_id: int, *, jpeg=False):
        client = MoebooruBase(self.site)
        info = client.pool_posts(id=pool_id)
        posts = info["posts"]
        imgs = []
        for post in posts:
            url = post["file_url"] if not jpeg else post["jpeg_url"]
            name, _ = self.parse_url(url)
            destination, filename = self.get_storage_dest(post, name)
            imgs.append(Image(filename, url, destination))
        caption = Caption({"name": info["name"], "description": info["description"]})
        return imgs, caption

    async def download_pool(self, pool_id, *, jpeg=False):
        imgs, caption = self.pool(pool_id, jpeg=jpeg)
        pool_name = caption["name"]
        await ensure_existence_async(os.path.join(TEMP_DIR, pool_name))
        for key, img in enumerate(imgs):
            filename = str(key + 1)
            filename = "0" * (3 - len(filename)) + filename
            _, ext = self.parse_url(img.url)
            filename += ext
            img.name = pool_name + "/" + img.name
            await img.download()  # TODO

    def get_images(self, post) -> List[Image]:
        file_url = post["file_url"]
        name, _ = self.parse_url(file_url)
        destination, filename = self.get_storage_dest(post, name)
        imgs = [
            Image(
                filename,
                file_url,
                destination,
                post["sample_url"],
                post["file_size"],
                post["width"],
                post["height"],
            ),
        ]
        return imgs

    def get_storage_dest(self, post: dict, filename: str) -> Tuple[str, str]:
        """
        Format destination and filename.
        """

        # `updated_at` is only available on yande.re, so we won't cover it here
        created_at = datetime.fromtimestamp(
            post["created_at"],
            tz=timezone.utc,
        )
        filename, extension = os.path.splitext(filename)
        # Site name in pascal case, i.e. Yandere, Konachan, Lolibooru
        site_name = snake_to_pascal(COLLECTIONS[self.url])
        context = {
            **post,
            # Original filename, without extension
            # Format may differ from site to site
            "filename": filename,
            "created_at": created_at,
            "extension": extension,
            "site_name": site_name,
            "site_url": self.url,
        }
        filename = FILENAME.format_map(context)
        return (DESTINATION.format_map(context), filename + extension)

    def build_caption(self, post, tags) -> Caption:
        """Build media caption from an post."""
        title = post["tags"]
        source = post["source"]
        tag_string = artists = ""
        for tag, tag_type in tags.items():
            if tag_type == "artist":
                artists += tag + " "
            else:
                tag_string += "#" + tag + " "
        caption = Caption(
            {
                "title": title,
                "artists": artists,
                "url": "https://" + self.url + "/post/show/" + str(post["id"]),
                "tags": tag_string,
                "source": source,
                "parent_id": post["parent_id"],
                "has_children": post["has_children"],
            },
        )
        return caption

    @staticmethod
    def parse_url(url: str) -> Tuple[str, str]:
        """
        Parse filename and extension from url.
        """

        name = unquote(os.path.basename(url))
        return name, os.path.splitext(name)[1]
