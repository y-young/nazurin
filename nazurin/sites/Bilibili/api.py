import json
import os
from typing import List

from nazurin.models import Image
from nazurin.utils import Request, downloadFiles

class Bilibili(object):
    async def getDynamic(self, dynamic_id: int):
        """Get dynamic data from API."""
        api = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id=' + str(
            dynamic_id)
        async with Request() as request:
            async with request.get(api) as response:
                source = await response.json()
        card = json.loads(source['data']['card']['card'])
        return card

    async def fetch(self, dynamic_id: int):
        """Fetch images and detail."""
        card = await self.getDynamic(dynamic_id)
        imgs = self.getImages(card, dynamic_id)
        await downloadFiles(imgs)
        return imgs, card

    def getImages(self, card, dynamic_id: int) -> List[Image]:
        """Get all images in a dynamic card."""
        pics = card['item']['pictures']
        imgs = list()
        for index, pic in enumerate(pics):
            url = pic['img_src']
            basename = os.path.basename(url)
            extension = os.path.splitext(basename)[1]
            imgs.append(
                Image(str(dynamic_id) + '_' + str(index) + extension, url))
        return imgs
