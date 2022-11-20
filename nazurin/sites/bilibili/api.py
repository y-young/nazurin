import json
import os
from datetime import datetime
from typing import List, Tuple

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

from .config import DESTINATION, FILENAME

class Bilibili:
    @network_retry
    async def get_dynamic(self, dynamic_id: int):
        """Get dynamic data from API."""
        api = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr'\
              '/get_dynamic_detail?dynamic_id=' + str(dynamic_id)
        async with Request() as request:
            async with request.get(api) as response:
                response.raise_for_status()
                data = await response.json()
                # For some IDs, the API returns code 0 but empty content
                if data['code'] == 500207 or (data['code'] == 0 and 'card'
                                              not in data['data'].keys()):
                    raise NazurinError('Dynamic not found')
                if data['code'] != 0:
                    raise NazurinError('Failed to get dynamic: ' +
                                       data['message'])
        card = data['data']['card']
        desc = card['desc']
        card = json.loads(card['card'])
        card.update({
            'type': desc['type'],
            'dynamic_id_str': desc['dynamic_id_str'],
            'view': desc['view'],
            'repost': desc['repost'],
            'comment': desc['comment'],
            'like': desc['like'],
            'timestamp': desc['timestamp'],
        })
        if 'vip' in card['user']:
            del card['user']['vip']
        return card

    async def fetch(self, dynamic_id: int) -> Illust:
        """Fetch images and detail."""
        card = await self.get_dynamic(dynamic_id)
        imgs = self.get_images(card)
        caption = self.build_caption(card)
        caption['url'] = f"https://t.bilibili.com/{dynamic_id}"
        return Illust(imgs, caption, card)

    @staticmethod
    def get_images(card) -> List[Image]:
        """Get all images in a dynamic card."""
        if 'item' not in card.keys() or 'pictures' not in card['item'].keys():
            raise NazurinError("No image found")
        pics = card['item']['pictures']
        imgs = []
        for index, pic in enumerate(pics):
            url = pic['img_src']
            destination, filename = Bilibili.get_storage_dest(card, pic, index)
            imgs.append(
                Image(
                    filename,
                    url,
                    destination,
                    url + '@518w.jpg',
                    pic['img_size'] * 1024,  # size returned by API is in KB
                    pic['img_width'],
                    pic['img_height']))
        return imgs

    @staticmethod
    def get_storage_dest(card: dict,
                         pic: dict,
                         index: int = 0) -> Tuple[str, str]:
        """
        Format destination and filename.
        """

        url = pic['img_src']
        timestamp = datetime.fromtimestamp(card['timestamp'])
        basename = os.path.basename(url)
        filename, extension = os.path.splitext(basename)
        context = {
            **card,
            # Original filename, without extension
            'filename': filename,
            # Image index
            'index': index,
            'timestamp': timestamp,
            'extension': extension,
            'pic': pic
        }
        return (DESTINATION.format_map(context),
                FILENAME.format_map(context) + extension)

    @staticmethod
    def build_caption(card) -> Caption:
        return Caption({
            'author': card['user']['name'],
            'content': card['item']['description']
        })
