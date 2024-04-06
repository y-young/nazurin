import os
import re
from datetime import datetime
from os import path
from typing import List, Optional, Tuple

from pybooru import Danbooru as DanbooruBase
from pybooru import PybooruHTTPError

from nazurin.models import Caption, File, Image
from nazurin.sites.danbooru.models import DanbooruIllust
from nazurin.utils.decorators import async_wrap
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import is_image

from .config import DESTINATION, FILENAME

MAX_CHARACTER_COUNT = 5


class Danbooru:
    def __init__(self, site="danbooru"):
        """Set Danbooru site."""
        self.site = site
        self.api = DanbooruBase(site)
        self.post_show = async_wrap(self.api.post_show)
        self.post_list = async_wrap(self.api.post_list)

    async def get_post(
        self,
        post_id: Optional[int] = None,
        md5: Optional[str] = None,
    ) -> dict:
        """Fetch a post."""
        try:
            if post_id:
                post = await self.post_show(post_id)
            else:
                post = await self.post_list(md5=md5)
        except PybooruHTTPError as err:
            # pylint: disable=protected-access
            if "Not Found" in err._msg:
                raise NazurinError("Post not found") from None
        if "file_url" not in post:
            raise NazurinError(
                "You may need a gold account to view this post\nSource: "
                + post["source"],
            )
        return post

    async def view(
        self,
        post_id: Optional[int] = None,
        md5: Optional[str] = None,
    ) -> DanbooruIllust:
        post = await self.get_post(post_id, md5)
        illust = self.parse_post(post)
        return illust

    def parse_post(self, post: dict) -> DanbooruIllust:
        """Get images and build caption."""
        # Get images
        url = post["file_url"]
        artists = post["tag_string_artist"]
        title, filename = self._get_names(post)
        imgs = []
        files = []
        destination, filename = self.get_storage_dest(post, filename)
        if is_image(url):
            imgs.append(
                Image(
                    filename,
                    url,
                    destination,
                    post["large_file_url"],
                    post["file_size"],
                    post["image_width"],
                    post["image_height"],
                ),
            )
        else:  # danbooru has non-image posts, such as #animated
            files.append(File(filename, url, destination))

        # Build media caption
        tags = post["tag_string"].split(" ")
        tag_string = ""
        for character in tags:
            tag_string += "#" + character + " "
        caption = Caption(
            {
                "title": title,
                "artists": artists,
                "url": "https://" + self.site + ".donmai.us/posts/" + str(post["id"]),
                "tags": tag_string,
                "parent_id": post["parent_id"],
                "pixiv_id": post["pixiv_id"],
                "has_children": post["has_children"],
            },
        )
        return DanbooruIllust(int(post["id"]), imgs, caption, post, files)

    @staticmethod
    def get_storage_dest(post: dict, filename: str) -> Tuple[str, str]:
        """
        Format destination and filename.
        """

        created_at = datetime.fromisoformat(post["created_at"])
        updated_at = datetime.fromisoformat(post["updated_at"])
        filename, extension = os.path.splitext(filename)
        context = {
            **post,
            # Human-friendly filename, without extension
            "filename": filename,
            "created_at": created_at,
            "updated_at": updated_at,
            "extension": extension,
        }
        return (
            DESTINATION.format_map(context),
            FILENAME.format_map(context) + extension,
        )

    @staticmethod
    def _get_names(post) -> Tuple[str, str]:
        """
        Build title and filename like that one when downloading on the website,
        usually in the form of "{characters} ({copyrights}) drawn by {artists}".
        """

        characters = Danbooru._format_characters(post["tag_string_character"])
        copyrights = Danbooru._format_copyrights(post["tag_string_copyright"])
        artists = Danbooru._format_artists(post["tag_string_artist"])
        extension = path.splitext(post["file_url"])[1]
        filename = ""

        if characters:
            filename += characters + " "
        if copyrights:
            if characters:
                copyrights = "(" + copyrights + ")"
            filename += copyrights + " "
        title = filename
        if artists:
            filename += "drawn by " + artists
        return title, filename + extension

    @staticmethod
    def _format_characters(characters: str) -> str:
        if not characters:
            return ""
        characters = characters.split(" ")
        characters = list(map(Danbooru._normalize, characters))
        size = len(characters)
        if size <= MAX_CHARACTER_COUNT:
            result = Danbooru._sentence(characters)
        else:
            characters = characters[:MAX_CHARACTER_COUNT]
            result = Danbooru._sentence(characters) + " and " + str(size - 1) + " more"
        return result

    @staticmethod
    def _format_copyrights(copyrights: str) -> str:
        if not copyrights:
            return ""
        copyrights = copyrights.split(" ")
        copyrights = list(map(Danbooru._normalize, copyrights))
        size = len(copyrights)
        if size == 1:
            result = copyrights[0]
        else:
            result = copyrights[0] + " and " + str(size - 1) + " more"
        return result

    @staticmethod
    def _format_artists(artists: str) -> str:
        if not artists:
            return ""
        return Danbooru._normalize(Danbooru._sentence(artists.split(" ")))

    @staticmethod
    def _sentence(names: List[str]) -> str:
        if len(names) == 1:
            return names[0]
        sentence = " ".join(names[:-1])
        sentence += " and " + names[-1]
        return sentence

    @staticmethod
    def _normalize(name: str) -> str:
        name = re.sub(r"_\(.*\)", "", name)  # replace _(...)
        name = name.replace("_", " ")
        name = re.sub(r"[\\\/]", " ", name)  # replace / and \
        return name
