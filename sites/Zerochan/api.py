import json
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
from models import Image
from requests.exceptions import HTTPError
from utils import NazurinError, downloadImages

class Zerochan(object):
    def getPost(self, post_id: int):
        response = requests.get('https://www.zerochan.net/' + str(post_id))
        try:
            response.raise_for_status()
        except HTTPError as err:
            raise NazurinError(err)

        # Override post_id if there's a redirection
        if response.history:
            post_id = response.url.split('/')[3]
        response = response.text
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

    def view(self, post_id: int):
        post = self.getPost(post_id)
        imgs = self.getImages(post)
        caption = self.buildCaption(post)
        return imgs, caption

    async def download(self,
                       post_id: Optional[int] = None,
                       post=None) -> List[Image]:
        if post:
            imgs = self.getImages(post)
        else:
            imgs, _ = self.view(post_id)
        await downloadImages(imgs)
        return imgs

    def getImages(self, post) -> List[Image]:
        url = post['file_url']
        name = 'Zerochan ' + str(
            post['id']) + ' ' + post['name'] + '.' + post['file_ext']
        return [Image(name, url)]

    def buildCaption(self, post):
        """Build media caption from an post."""
        details = dict()
        details['title'] = post['name']
        tag_string = artists = source = str()
        for tag, tag_type in post['tags'].items():
            if tag_type == 'Mangaka':
                artists += tag + ' '
            elif tag_type == 'Source':
                source += tag + ' '
            else:
                tag_string += '#' + tag + ' '
        if artists:
            details['artists'] = artists
        details['url'] = 'https://www.zerochan.net/' + str(post['id'])
        if source:
            details['source'] = source
        if tag_string:
            details['tags'] = tag_string
        return details
