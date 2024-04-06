import os
from datetime import datetime
from http import HTTPStatus
from typing import List, Tuple

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

from .config import API_KEY, DESTINATION, FILENAME


class Wallhaven:
    @network_retry
    async def get_wallpaper(self, wallpaper_id: str):
        """Get wallpaper information from API."""
        api = "https://wallhaven.cc/api/v1/w/" + wallpaper_id
        if API_KEY:
            api += "?apikey=" + API_KEY
        async with Request() as request, request.get(api) as response:
            if response.status == HTTPStatus.NOT_FOUND:
                raise NazurinError("Wallpaper doesn't exist.")
            if response.status == HTTPStatus.UNAUTHORIZED:
                raise NazurinError(
                    (
                        "You need to log in to view this wallpaper. "
                        "Please ensure that you have set a valid API key."
                    ),
                )
            response.raise_for_status()
            wallpaper = await response.json()
            if "error" in wallpaper:
                raise NazurinError(wallpaper["error"])
            return wallpaper["data"]

    async def fetch(self, wallpaper_id: str) -> Illust:
        """Fetch & return wallpaper image and information."""
        wallpaper = await self.get_wallpaper(wallpaper_id)
        imgs = self.get_images(wallpaper)
        caption = self.build_caption(wallpaper)
        return Illust(wallpaper_id, imgs, caption, wallpaper)

    @staticmethod
    def get_images(wallpaper) -> List[Image]:
        url = wallpaper["path"]
        thumbnail = wallpaper["thumbs"]["large"]
        destination, filename = Wallhaven.get_storage_dest(wallpaper)
        return [
            Image(
                filename,
                url,
                destination,
                thumbnail,
                wallpaper["file_size"],
                wallpaper["dimension_x"],
                wallpaper["dimension_y"],
            ),
        ]

    @staticmethod
    def get_storage_dest(wallpaper: dict) -> Tuple[str, str]:
        """
        Format destination and filename.
        """

        # Wallhaven uses UTC time
        created_at = datetime.fromisoformat(wallpaper["created_at"] + "+00:00")
        _, extension = os.path.splitext(os.path.basename(wallpaper["path"]))
        context = {**wallpaper, "created_at": created_at, "extension": extension}
        filename = FILENAME.format_map(context)
        return (DESTINATION.format_map(context), filename + extension)

    @staticmethod
    def build_caption(wallpaper) -> Caption:
        tags = ""
        for tag in wallpaper["tags"]:
            tags += "#" + tag["name"].strip().replace(" ", "_") + " "
        return Caption(
            {"url": wallpaper["url"], "source": wallpaper["source"], "tags": tags},
        )
