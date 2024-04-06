import json
import os
from datetime import datetime
from typing import List, Tuple
from urllib.parse import unquote

from bs4 import BeautifulSoup

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry

from .config import DESTINATION, FILENAME


class Zerochan:
    @network_retry
    async def get_post(self, post_id: int):
        async with Request() as request, request.get(
            "https://www.zerochan.net/" + str(post_id),
        ) as response:
            response.raise_for_status()

            # Override post_id if there's a redirection TODO: Check
            if response.history:
                post_id = response.url.path[1:]
            response_text = await response.text()

        soup = BeautifulSoup(response_text, "html.parser")
        info = soup.find("script", {"type": "application/ld+json"}).contents
        info = json.loads("".join(info).replace("\\'", "'"))

        name = info["name"].split(" #")[0]
        created_at = info["datePublished"]
        size = int(info["contentSize"][:-2]) * 1024
        tags = {}
        for tag in soup.find("ul", id="tags").find_all("li"):
            tag_type = " ".join(tag["class"]).title()
            tag_name = unquote(tag.find("a")["href"][1:]).replace("+", "_")
            tags[tag_name] = tag_type
        post = {
            "id": int(post_id),
            "name": name,
            "created_at": created_at,
            "image_width": info["width"][:-3],
            "image_height": info["height"][:-3],
            "tags": tags,
            "file_ext": info["encodingFormat"],
            "file_size": size,
            "file_url": info["contentUrl"],
            "preview_file_url": info["thumbnail"],
            "uploader": info["author"],
        }
        return post

    async def view(self, post_id: int) -> Illust:
        post = await self.get_post(post_id)
        imgs = self.get_images(post)
        caption = self.build_caption(post)
        return Illust(post_id, imgs, caption, post)

    @staticmethod
    def get_images(post) -> List[Image]:
        url = post["file_url"]
        destination, filename = Zerochan.get_storage_dest(post)
        return [
            Image(
                filename,
                url,
                destination,
                post["preview_file_url"],
                post["file_size"],
                int(post["image_width"]),
                int(post["image_height"]),
            ),
        ]

    @staticmethod
    def get_storage_dest(post: dict) -> Tuple[str, str]:
        """
        Format destination and filename.
        """

        created_at = datetime.fromisoformat(post["created_at"])
        filename, extension = os.path.splitext(os.path.basename(post["file_url"]))
        context = {
            **post,
            "created_at": created_at,
            # Original filename, without extension
            "filename": filename,
            "extension": extension,
        }
        filename = FILENAME.format_map(context)
        return (DESTINATION.format_map(context), filename + extension)

    @staticmethod
    def build_caption(post) -> Caption:
        """Build media caption from an post."""
        tag_string = artists = source = ""
        for tag, tag_type in post["tags"].items():
            if tag_type == "Mangaka":
                artists += tag + " "
            elif tag_type == "Source":
                source += tag + " "
            else:
                tag_string += "#" + tag + " "
        caption = Caption(
            {
                "title": post["name"],
                "artists": artists,
                "url": "https://www.zerochan.net/" + str(post["id"]),
                "source": source,
                "tags": tag_string,
            },
        )
        return caption
