from typing import List

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

class miHoYoBBS(object):
    @network_retry
    async def getPost(self, post_id: int):
        """Fetch a post."""
        api = 'https://bbs-api.mihoyo.com/post/api/getPostFull?post_id=' + str(post_id)
        async with Request(
                headers={'Referer': 'https://app.mihoyo.com'}) as request:
            async with request.get(api) as response:
                response.raise_for_status()
                data = await response.json()
                if data['retcode'] != 0:
                    raise NazurinError(data['message'])

                post = data['data']['post']
                return post

    async def fetch(self, post_id: str) -> Illust:
        post = await self.getPost(post_id)
        imgs = self.getImages(post)
        caption = self.buildCaption(post)
        return Illust(imgs, caption, post)

    def getImages(self, post: dict) -> List[Image]:
        """Get images from post."""
        if ('image_list' not in post.keys()) or (
                'images' not in post['post'].keys()):

            raise NazurinError('No images found.')

        pics = post['image_list']
        imgs = list()
        for index, pic in enumerate(pics):
            url = pic['url']
            extension = pic['format']
            if extension == 'gif':
                continue

            thumbnail = url + f"?x-oss-process=image//resize,s_800/quality,q_80/auto-orient,0/interlace,1/format,{extension}"
            filename = f"miHoYoBBS - {post['post_id']}_{index}.{extension}"
            imgs.append(
                Image(filename,
                      url,
                      thumbnail,
                      width=pic['width'],
                      height=pic['height']))
        return imgs

    def buildCaption(self, post) -> Caption:
        #https://github.com/y1ndan/genshinhelper2/blob/main/genshinhelper/mihoyo.py#L183
        game_ids = {1: '崩坏3', 2: '原神', 3: '崩坏2', 4: '未定事件簿', 5: '大别野', 6: '崩坏: 星穹铁道', 8: '绝区零'}
        game_ids_abbr = {1: 'bh3', 2: 'ys', 3: 'bh2', 4: 'wd', 5: 'dby', 6: 'sr', 8: 'zzz'}

        tags = post['topics']
        tag_string = str()
        for tag in tags:
            tag_string += '#' + tag['name'] + ' '

        return Caption({
            'forum': game_ids[post['forum']['game_id']],
            'title': post['post']['subject'],
            'author': post['user']['nickname'],
            'url': f"https://bbs.mihoyo.com/{game_ids_abbr[post['forum']['game_id']]}/article/{post['post']['post_id']}",
            'tags': tag_string
        })