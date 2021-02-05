from typing import List

from nazurin.models import Image
from nazurin.utils import Request, downloadFiles
from nazurin.utils.exceptions import NazurinError

class Gelbooru(object):
    async def getPost(self, post_id: int):
        """Fetch an post."""
        api = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id=' + str(
            post_id)
        async with Request() as request:
            async with request.get(api) as response:
                if not response.text:
                    raise NazurinError('Post not found')
                response = await response.json()
                post = response[0]
                return post

    async def fetch(self, post_id: int):
        post = await self.getPost(post_id)
        imgs = self.getImages(post)
        await downloadFiles(imgs)
        return imgs, post

    def getImages(self, post) -> List[Image]:
        """Get images from post."""
        url = post['file_url']
        ext = post['image'].split('.')[1]
        filename = 'gelbooru - ' + str(post['id']) + '.' + ext
        imgs = list()
        imgs.append(Image(filename, url))
        return imgs
