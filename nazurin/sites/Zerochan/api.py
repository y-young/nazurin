import json
from datetime import datetime, timezone
from typing import List
from urllib.parse import unquote

from aiohttp.client_exceptions import ClientResponseError
from bs4 import BeautifulSoup

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.exceptions import NazurinError

class Zerochan(object):
    async def getPost(self, post_id: int):
        async with Request() as request:
            async with request.get('https://www.zerochan.net/' +
                                   str(post_id)) as response:
                try:
                    response.raise_for_status()
                except ClientResponseError as err:
                    raise NazurinError(err) from None

                # Override post_id if there's a redirection TODO: Check
                if response.history:
                    post_id = response.url.path[1:]
                response = await response.text()

        soup = BeautifulSoup(response, 'html.parser')
        info = soup.find("script", {"type": "application/ld+json"}).contents
        info = json.loads(''.join(info).replace('\\\'', '\''))

        name = info['name'].split(' #')[0]
        created_at = int(
            datetime.strptime(info['datePublished'],
                              '%c').replace(tzinfo=timezone.utc).timestamp())
        size = int(info['contentSize'][:-2]) * 1024
        tags = dict()
        for tag in soup.find('ul', id='tags').find_all('li'):
            tag_name, tag_type = tag.contents
            tag_name = unquote(tag_name['href'][1:]).replace('+', '_')
            tag_type = tag_type[1:]
            tags[tag_name] = tag_type
        post = {
            'id': int(post_id),
            'name': name,
            'created_at': created_at,
            'image_width': info['width'][:-3],
            'image_height': info['height'][:-3],
            'tags': tags,
            'file_ext': info['encodingFormat'],
            'file_size': size,
            'file_url': info['contentUrl'],
            'preview_file_url': info['thumbnail'],
            'uploader': info['author']
        }
        return post

    async def view(self, post_id: int) -> Illust:
        post = await self.getPost(post_id)
        imgs = self.getImages(post)
        caption = self.buildCaption(post)
        return Illust(imgs, caption, post)

    def getImages(self, post) -> List[Image]:
        url = post['file_url']
        name = 'Zerochan ' + str(
            post['id']) + ' ' + post['name'] + '.' + post['file_ext']
        return [Image(name, url)]

    def buildCaption(self, post) -> Caption:
        """Build media caption from an post."""
        tag_string = artists = source = str()
        for tag, tag_type in post['tags'].items():
            if tag_type == 'Mangaka':
                artists += tag + ' '
            elif tag_type == 'Source':
                source += tag + ' '
            else:
                tag_string += '#' + tag + ' '
        caption = Caption({
            'title': post['name'],
            'artists': artists,
            'url': 'https://www.zerochan.net/' + str(post['id']),
            'source': source,
            'tags': tag_string
        })
        return caption
