import json
import os
import re
from typing import List, Tuple

from nazurin.models import Caption
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import fromasctimeformat

from .config import DESTINATION, FILENAME
from .models import WeiboIllust, WeiboImage


class Weibo:
    @network_retry
    async def get_post(self, post_id: str):
        """Fetch a post."""
        api = f"https://m.weibo.cn/detail/{post_id}"
        async with Request() as request, request.get(api) as response:
            response.raise_for_status()
            html = await response.text()
            post = self.parse_html(html)
            return post

    async def fetch(self, post_id: str) -> WeiboIllust:
        post = await self.get_post(post_id)
        imgs = self.get_images(post)
        caption = self.build_caption(post)
        return WeiboIllust(
            int(post["mid"]),
            imgs,
            caption,
            post,
            referer=f"https://m.weibo.cn/detail/{post_id}",
        )

    def get_images(self, post) -> List[WeiboImage]:
        """Get images from post."""
        if "pics" not in post:
            raise NazurinError("No image found")
        pics = post["pics"]
        imgs = []
        for index, pic in enumerate(pics):
            url, thumbnail, width, height = self.parse_pic(pic)
            destination, filename = self.get_storage_dest(post, pic, index)
            imgs.append(
                WeiboImage(
                    filename,
                    url,
                    destination,
                    thumbnail,
                    width=width,
                    height=height,
                    referer=f"https://m.weibo.cn/detail/{post['mid']}",
                ),
            )
        return imgs

    @staticmethod
    def get_storage_dest(post: dict, pic: dict, index: int) -> Tuple[str, str]:
        """
        Format destination and filename.
        """

        created_at = fromasctimeformat(post["created_at"])
        _, extension = os.path.splitext(os.path.basename(pic["url"]))
        context = {
            **post,
            "pic": pic,
            "created_at": created_at,
            "index": index,
            "extension": extension,
        }
        filename = FILENAME.format_map(context)
        return (DESTINATION.format_map(context), filename + extension)

    def build_caption(self, post) -> Caption:
        user = post["user"]
        tags = self.get_tags(post)
        tag_string = ""
        for tag in tags:
            tag_string += "#" + tag + " "
        return Caption(
            {
                "title": post["status_title"],
                "author": f"#{user['screen_name']}",
                "desktop_url": f"https://weibo.com/{user['id']}/{post['bid']}",
                "mobile_url": f"https://m.weibo.cn/detail/{post['mid']}",
                "tags": tag_string,
            },
        )

    @staticmethod
    def get_tags(post) -> List[str]:
        if "text" not in post or not post["text"]:
            return []
        regex = r"#(\S+)#"
        matches = re.findall(regex, post["text"], re.MULTILINE)
        if not matches:
            return []
        return matches

    @staticmethod
    def parse_pic(pic: dict) -> Tuple[str, str, str, int, int]:
        """Get original file url & thumbnail url of the picture

        eg:
        ```json
            {
                "pid": "001Y6PUIgy1gvre6rshhbj61iv0zmdlw02",
                "url":\
                    "https://wx3.sinaimg.cn/orj360/001Y6PUIgy1gvre6rshhbj61iv0zmdlw02.jpg",
                "size": "orj360",
                "geo": {
                    "width": 415,
                    "height": 270,
                    "croped": false
                },
                "large": {
                    "size": "large",
                    "url":\
                        "https://wx3.sinaimg.cn/large/001Y6PUIgy1gvre6rshhbj61iv0zmdlw02.jpg",
                    "geo": {
                        "width": "1975",
                        "height": "1282",
                        "croped": false
                    }
                }
            }
        ```

        return:
            'https://wx3.sinaimg.cn/large/001Y6PUIgy1gvre6rshhbj61iv0zmdlw02.jpg',
            'https://wx3.sinaimg.cn/orj360/001Y6PUIgy1gvre6rshhbj61iv0zmdlw02.jpg',
            1975,
            1282
        """
        thumbnail = pic["url"]
        url = pic["large"]["url"]
        width = int(pic["large"]["geo"]["width"])
        height = int(pic["large"]["geo"]["height"])
        return url, thumbnail, width, height

    @staticmethod
    def parse_html(html) -> dict:
        """
        Extract post data from html <script> block as example below.
        We're lucky the JS objects are written in JSON syntax
        with quotes wrapped property names.

        <script>
        ...
        var $render_data = [{
            "status": {
                ...
            }, ...
        }][0] || {};
        ...
        </script>
        """
        regex = r"\$render_data = \[\{\n([\s\S]+)\}\]\[0\] \|\| \{\};"
        matches = re.search(regex, html, re.MULTILINE)
        if not matches:
            raise NazurinError("Post not found")
        json_str = "[{" + matches.group(1) + "}]"
        try:
            render_data = json.loads(json_str)
            post = render_data[0]["status"]
        except json.JSONDecodeError:
            raise NazurinError("Failed to parse post data") from None
        return post
