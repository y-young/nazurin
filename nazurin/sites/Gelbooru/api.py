from typing import List

import requests

from nazurin.models import Image
from nazurin.utils import NazurinError, downloadImages


class Gelbooru(object):
    def getPost(self, post_id: int):
        """Fetch an post."""
        api = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id=' + str(
            post_id)
        response = requests.get(api)
        if not response.text:
            raise NazurinError('Post not found')
        post = response.json()[0]
        return post

    async def fetch(self, post_id: int):
        post = self.getPost(post_id)
        imgs = self.getImages(post)
        await downloadImages(imgs)
        return imgs, post

    def getImages(self, post) -> List[Image]:
        """Get images from post."""
        url = post['file_url']
        ext = post['image'].split('.')[1]
        filename = 'gelbooru - ' + str(post['id']) + '.' + ext
        imgs = list()
        imgs.append(Image(filename, url))
        return imgs
