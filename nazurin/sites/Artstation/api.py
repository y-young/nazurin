import os
from typing import List, Tuple

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

class Artstation:
    @network_retry
    async def get_post(self, post_id: str):
        """Fetch a post."""
        api = f"https://www.artstation.com/projects/{post_id}.json"
        async with Request() as request:
            async with request.get(api) as response:
                if response.status == 404:
                    raise NazurinError('Post not found')
                response.raise_for_status()
                post = await response.json()
                return post

    async def fetch(self, post_id: str) -> Illust:
        post = await self.get_post(post_id)
        imgs = self.get_images(post)
        caption = self.build_caption(post)
        return Illust(imgs, caption, post)

    def get_images(self, post) -> List[Image]:
        """Get images from post."""
        if 'assets' not in post.keys():
            raise NazurinError('No asset found.')
        assets = sorted(post['assets'], key=lambda x: x['position'])
        hash_id = post['hash_id']
        imgs = list()
        for asset in assets:
            if asset['asset_type'] != 'image':
                continue
            # https://cdnb.artstation.com/p/assets/images/images/042/908/363/large/_z-ed_-da.jpg?1635784439
            filename, url, thumbnail = self.parse_url(asset['image_url'])
            imgs.append(
                Image(f"ArtStation - {hash_id} - {filename}",
                      url,
                      thumbnail,
                      width=asset['width'],
                      height=asset['height']))
        return imgs

    @staticmethod
    def build_caption(post) -> Caption:
        user = post['user']
        tags = post['tags']
        tag_string = str()
        for tag in tags:
            tag_string += '#' + tag + ' '
        return Caption({
            'title': post['title'],
            'author': f"{user['full_name']} #{user['username']}",
            'url': f"https://www.artstation.com/artwork/{post['hash_id']}",
            'tags': tag_string,
        })

    @staticmethod
    def parse_url(src: str) -> Tuple[str, str, str]:
        """Get filename, original file url & thumbnail url of the original image

        eg:
        - src: 'https://cdnb.artstation.com/p/assets/images/images/042/908/363/large/_z-ed_-da.jpg'

        - return:
            '_z-ed_-da.jpg',
            'https://cdnb.artstation.com/p/assets/images/images/042/908/363/4k/_z-ed_-da.jpg',
            'https://cdnb.artstation.com/p/assets/images/images/042/908/363/medium/_z-ed_-da.jpg'

        """
        baseurl = src.split('?')[0]
        basename = os.path.basename(baseurl)
        url = baseurl.replace('/large/', '/4k/')
        thumbnail = baseurl.replace('/large/', '/medium/')
        return basename, url, thumbnail
