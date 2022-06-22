import os
from typing import List

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

from .config import API_KEY

class Wallhaven(object):
    @network_retry
    async def get_wallpaper(self, wallpaper_id: str):
        """Get wallpaper information from API."""
        api = 'https://wallhaven.cc/api/v1/w/' + wallpaper_id
        if API_KEY:
            api += '?apikey=' + API_KEY
        async with Request() as request:
            async with request.get(api) as response:
                if response.status == 404:
                    raise NazurinError("Wallpaper doesn't exist.")
                if response.status == 401:
                    raise NazurinError(
                        'You need to log in to view this wallpaper. ' +
                        'Please ensure that you have set a valid API key.')
                response.raise_for_status()
                wallpaper = await response.json()
                if 'error' in wallpaper.keys():
                    raise NazurinError(wallpaper['error'])
                return wallpaper['data']

    async def fetch(self, wallpaper_id: str) -> Illust:
        """Fetch & return wallpaper image and information."""
        wallpaper = await self.get_wallpaper(wallpaper_id)
        imgs = self.get_images(wallpaper)
        caption = self.build_caption(wallpaper)
        return Illust(imgs, caption, wallpaper)

    def get_images(self, wallpaper) -> List[Image]:
        url = wallpaper['path']
        filename = os.path.basename(url)
        thumbnail = wallpaper['thumbs']['large']
        return [
            Image(filename, url, thumbnail, wallpaper['file_size'],
                  wallpaper['dimension_x'], wallpaper['dimension_y'])
        ]

    def build_caption(self, wallpaper) -> Caption:
        tags = str()
        for tag in wallpaper['tags']:
            tags += '#' + tag['name'].strip().replace(' ', '_') + ' '
        return Caption({
            'url': wallpaper['url'],
            'source': wallpaper['source'],
            'tags': tags
        })
