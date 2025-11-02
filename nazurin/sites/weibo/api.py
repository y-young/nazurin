import json
import os
import re
from typing import ClassVar

from nazurin.models import Caption
from nazurin.utils import Request, logger
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import fromasctimeformat

from .config import DESTINATION, FILENAME
from .models import WeiboIllust, WeiboImage


class Weibo:
    tid: ClassVar[str] = ""
    cookies: ClassVar[dict] = {}

    VISITOR_SYSTEM_SUCCESS_CODE: ClassVar[int] = 20000000

    @network_retry
    async def get_post(self, post_id: str):
        """Fetch a post."""
        post_url = f"https://m.weibo.cn/detail/{post_id}"
        async with (
            Request(cookies=Weibo.cookies) as request,
            request.get(post_url) as response,
        ):
            if response.url.host == "visitor.passport.weibo.cn":
                logger.info("Handling Weibo visitor system: {}", response.url)
                await self._handle_visitor_system(post_url, str(response.url))
                async with (
                    Request(cookies=Weibo.cookies) as new_request,
                    new_request.get(post_url) as new_response,
                ):
                    new_response.raise_for_status()
                    html = await new_response.text()
            else:
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

    def get_images(self, post) -> list[WeiboImage]:
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
    def get_storage_dest(post: dict, pic: dict, index: int) -> tuple[str, str]:
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
    def get_tags(post) -> list[str]:
        if "text" not in post or not post["text"]:
            return []
        regex = r"#(\S+)#"
        matches = re.findall(regex, post["text"], re.MULTILINE)
        if not matches:
            return []
        return matches

    @staticmethod
    def parse_pic(pic: dict) -> tuple[str, str, str, int, int]:
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

    async def _handle_visitor_system(
        self, post_url: str, visitor_system_url: str
    ) -> None:
        token_url = "https://visitor.passport.weibo.cn/visitor/genvisitor2"
        payload = {
            "cb": "visitor_gray_callback",
            "ver": "20250916",
            "tid": Weibo.tid,
            "from": "weibo",
            "webdriver": "false",
            "return_url": post_url,
        }
        async with (
            Request(
                headers={
                    "Referer": visitor_system_url,
                }
            ) as request,
            request.post(token_url, data=payload) as response,
        ):
            if not response.ok:
                message = (
                    "Weibo visitor system token request failed "
                    f"with status code {response.status}"
                )
                logger.error(
                    "{}: {}",
                    message,
                    await response.text(),
                )
                raise NazurinError(message)
            match = re.search(
                r"visitor_gray_callback\((.*?)\);",
                await response.text(),
                re.MULTILINE,
            )
            try:
                data = json.loads(match.group(1)) if match else None
            except json.JSONDecodeError:
                data = None
            if not data or data.get("retcode") != Weibo.VISITOR_SYSTEM_SUCCESS_CODE:
                logger.error(
                    "Failed to handle Weibo visitor system, response: {}",
                    await response.text(),
                )
                raise NazurinError("Failed to get token from Weibo visitor system")
            Weibo.tid = data["data"]["tid"]
            Weibo.cookies = {
                "tid": Weibo.tid,
                "SUB": data["data"]["sub"],
                "SUBP": data["data"]["subp"],
            }
            logger.info("Successfully got token from Weibo visitor system")
