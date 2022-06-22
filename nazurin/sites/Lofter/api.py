import json
import os
from typing import List, Tuple
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

class Lofter:
    @network_retry
    async def get_post(self, username: str, permalink: str) -> dict:
        """Fetch a post."""
        (blog_id, post_id) = await self.get_real_id(username, permalink)
        API = 'https://api.lofter.com/oldapi/post/detail.api'
        UA = 'LOFTER/6.24.0 (iPhone; iOS 15.4.1; Scale/3.00)'
        async with Request(headers={'User-Agent': UA}) as request:
            async with request.post(API,
                                    data={
                                        'targetblogid': blog_id,
                                        'postid': post_id,
                                    }) as response:
                response.raise_for_status()

                data = await response.json()
                if data['meta']['status'] != 200:
                    raise NazurinError(data['meta']['msg'])

                post = data['response']['posts'][0]['post']
                return post

    async def fetch(self, username: str, permalink: str) -> Illust:
        post = await self.get_post(username, permalink)
        imgs = self.get_images(post)
        caption = Caption({
            'author': f"{post['blogInfo']['blogNickName']} #{post['blogInfo']['blogName']}",
            'url': post['blogPageUrl'],
            'tags': ' '.join(["#" + tag for tag in post['tagList']])
        })
        return Illust(imgs, caption, post)

    @staticmethod
    def get_images(post: dict) -> List[Image]:
        """Get images from post."""
        if 'photoLinks' not in post.keys():
            raise NazurinError('No images found')

        photos = json.loads(post['photoLinks'])
        imgs = list()
        for (index, photo) in enumerate(photos):
            url = photo['raw']
            ext = os.path.splitext(url)[1]
            filename = f"Lofter - {post['id']}_{index}{ext}"
            imgs.append(
                Image(filename,
                      url,
                      thumbnail=photo['orign'],
                      width=photo['rw'],
                      height=photo['rh']))
        return imgs

    @network_retry
    async def get_real_id(self, username: str,
                          post_id: str) -> Tuple[int, int]:
        """Get real numeric blog ID and post ID."""
        api = f"https://{username}.lofter.com/post/{post_id}"
        async with Request() as request:
            async with request.get(api) as response:
                if response.status == 404:
                    raise NazurinError('Post not found')
                response.raise_for_status()

                response = await response.text()
                soup = BeautifulSoup(response, 'html.parser')
                iframe = soup.find('iframe', id='control_frame')
                if not iframe:
                    raise NazurinError('Failed to get real post ID')
                src = urlparse(iframe.get('src'))
                query = parse_qs(src.query)
                return (query['blogId'][0], query['postId'][0])
