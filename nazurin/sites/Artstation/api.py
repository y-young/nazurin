import os
from typing import List, Tuple

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.exceptions import NazurinError

class Artstation(object):
    async def getPost(self, post_id: int):
        """Fetch an post."""
        api = f"https://www.artstation.com/projects/{post_id}.json"
        async with Request() as request:
            async with request.get(api) as response:
                if not response.text:
                    raise NazurinError('Post not found')
                post = await response.json()
                return post

    async def fetch(self, post_id: int) -> Illust:
        post = await self.getPost(post_id)
        imgs = self.getImages(post)
        caption = self.buildCaption(post)
        return Illust(imgs, caption, post)

    def getImages(self, post) -> List[Image]:
        """Get images from post."""
        if 'assets' not in post.keys():
            raise NazurinError('No asset found.')
        assets = sorted(post['assets'], key=lambda x: x['position'])
        imgs = list()
        for asset in assets:
            if asset['asset_type'] != 'image':
                continue
            # https://cdnb.artstation.com/p/assets/images/images/042/908/363/large/_z-ed_-da.jpg?1635784439
            filename, url, thumbnail = self.parseUrl(asset['image_url'])
            imgs.append(
                Image(filename,
                      url,
                      thumbnail,
                      width=asset['width'],
                      height=asset['height']))
        return imgs

    def buildCaption(self, post) -> Caption:
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

    def parseUrl(self, src: str) -> Tuple[str, str, str]:
        """Get filename, original file url & thumbnail url of the original image

        eg:

            src: 'https://cdnb.artstation.com/p/assets/images/images/042/908/363/large/_z-ed_-da.jpg?1635784439'

            return:
                '_z-ed_-da.jpg',
                'https://cdnb.artstation.com/p/assets/images/images/042/908/363/large/_z-ed_-da.jpg',
                'https://cdnb.artstation.com/p/assets/images/images/042/908/363/small_square/_z-ed_-da.jpg'

        """
        baseurl = src.split('?')[0]
        basename = os.path.basename(baseurl)
        thumbnail = baseurl.replace('/large/', '/small_square/')
        return basename, baseurl, thumbnail