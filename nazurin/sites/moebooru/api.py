import json
import os
from typing import List, Optional
from urllib.parse import unquote

from aiohttp.client_exceptions import ClientResponseError
from bs4 import BeautifulSoup
from pybooru import Moebooru as moebooru

from nazurin.config import TEMP_DIR
from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request, logger
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import ensure_existence

class Moebooru:
    def __init__(self):
        self.url = 'yande.re'

    def site(self, site_url: Optional[str] = 'yande.re'):
        self.url = site_url
        return self

    @network_retry
    async def get_post(self, post_id: int):
        url = 'https://' + self.url + '/post/show/' + str(post_id)
        async with Request() as request:
            async with request.get(url) as response:
                try:
                    response.raise_for_status()
                except ClientResponseError as err:
                    raise NazurinError(err) from None
                response = await response.text()
        soup = BeautifulSoup(response, 'html.parser')
        tag = soup.find(id="post-view").find(recursive=False)
        if tag.name == 'script':
            content = str.strip(tag.string)
        elif tag.name == 'div' and ('status-notice' in tag['class']):
            raise NazurinError(tag.get_text(strip=True))
        else:
            logger.error(tag)
            raise NazurinError('Unknown error')

        info = content[19:-2]
        try:
            info = json.loads(info)
            post = info['posts'][0]
            tags = info['tags']
        except json.decoder.JSONDecodeError as err:
            logger.error(err)
        return post, tags

    async def view(self, post_id: int) -> Illust:
        post, tags = await self.get_post(post_id)
        imgs = self.get_images(post)
        caption = self.build_caption(post, tags)
        return Illust(imgs, caption, post)

    def pool(self, pool_id: int, jpeg=False):
        client = moebooru(self.site)
        info = client.pool_posts(id=pool_id)
        posts = info['posts']
        imgs = list()
        for post in posts:
            if not jpeg:
                url = post['file_url']
            else:
                url = post['jpeg_url']
            name, _ = self.parse_url(url)
            imgs.append(Image(name, url))
        caption = Caption({
            'name': info['name'],
            'description': info['description']
        })
        return imgs, caption

    async def download_pool(self, pool_id, jpeg=False):
        imgs, caption = self.pool(pool_id, jpeg)
        pool_name = caption['name']
        ensure_existence(os.path.join(TEMP_DIR, pool_name))
        for key, img in enumerate(imgs):
            filename = str(key + 1)
            filename = '0' * (3 - len(filename)) + filename
            _, ext = self.parse_url(img.url)
            filename += ext
            img.name = pool_name + '/' + img.name
            await img.download()  # TODO

    @staticmethod
    def get_images(post) -> List[Image]:
        file_url = post['file_url']
        name = unquote(os.path.basename(file_url))
        imgs = [
            Image(name, file_url, post['sample_url'], post['file_size'],
                  post['width'], post['height'])
        ]
        return imgs

    def build_caption(self, post, tags) -> Caption:
        """Build media caption from an post."""
        title = post['tags']
        source = post['source']
        tag_string = artists = str()
        for tag, tag_type in tags.items():
            if tag_type == 'artist':
                artists += tag + ' '
            else:
                tag_string += '#' + tag + ' '
        caption = Caption({
            'title': title,
            'artists': artists,
            'url': 'https://' + self.url + '/post/show/' + str(post['id']),
            'tags': tag_string,
            'source': source,
            'parent_id': post['parent_id'],
            'has_children': post['has_children']
        })
        return caption

    @staticmethod
    def parse_url(url: str) -> str:
        name = os.path.basename(url)
        return os.path.splitext(name)
