from typing import List, Optional
from urllib.parse import urlparse

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.exceptions import NazurinError

from .config import DESTINATION

class Gelbooru:
    async def get_post(self, post_id: int):
        """Fetch an post."""
        api = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id=' + str(
            post_id)
        async with Request() as request:
            async with request.get(api) as response:
                response.raise_for_status()
                response = await response.json()
                if 'post' not in response.keys():
                    raise NazurinError('Post not found')
                post = response['post'][0]
                return post

    async def fetch(self, post_id: int) -> Illust:
        post = await self.get_post(post_id)
        imgs = self.get_images(post)
        caption = self.build_caption(post)
        return Illust(imgs, caption, post)

    def get_images(self, post) -> List[Image]:
        """Get images from post."""
        url = post['file_url']
        ext = post['image'].split('.')[1]
        filename = 'gelbooru - ' + str(post['id']) + '.' + ext
        imgs = list()
        imgs.append(
            Image(filename,
                  url,
                  DESTINATION,
                  self.get_thumbnail(post),
                  width=post['width'],
                  height=post['height']))
        return imgs

    @staticmethod
    def build_caption(post) -> Caption:
        tags = post['tags'].split(' ')
        tag_string = str()
        for tag in tags:
            tag_string += '#' + tag + ' '
        return Caption({
            'title': post['title'],
            'source': post['source'],
            'url': f"https://gelbooru.com/index.php?page=post&s=view&id={post['id']}",
            'tags': tag_string
        })

    @staticmethod
    def get_thumbnail(post) -> Optional[str]:
        """
        Get thumbnail URL from post['file_url'].
        eg:
        https://img3.gelbooru.com/images/a1/b2/12ab34cd56ef7890ab12cd34ef567890.jpg ->
        https://img3.gelbooru.com/samples/a1/b2/sample_12ab34cd56ef7890ab12cd34ef567890.jpg
        """

        if post['sample'] != 1:
            return None
        url = urlparse(post['file_url'])
        return f"{url.scheme}://{url.netloc}/samples/{post['directory']}/sample_{post['image']}"
