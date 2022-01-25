import json
import os
import re
from typing import List, Optional
from urllib.parse import unquote

from aiohttp.client_exceptions import ClientResponseError
from bs4 import BeautifulSoup
from pybooru import Moebooru as moebooru

from nazurin.config import TEMP_DIR
from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request, logger
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import ensureExistence


class Moebooru(object):
    def site(self, site_url: Optional[str] = "yande.re"):
        self.url = site_url
        return self

    async def getPost(self, post_id: int):
        url = "https://" + self.url + "/post/show/" + str(post_id)
        async with Request() as request:
            async with request.get(url) as response:
                try:
                    response.raise_for_status()
                except ClientResponseError as err:
                    raise NazurinError(err) from None
                response = await response.text()
        soup = BeautifulSoup(response, "html.parser")
        tag = soup.find(id="post-view").find(recursive=False)
        if tag.name == "script":
            content = str.strip(tag.string)
        elif tag.name == "div" and ("status-notice" in tag["class"]):
            raise NazurinError(tag.get_text(strip=True))
        else:
            logger.error(tag)
            raise NazurinError("Unknown error")

        info = content[19:-2]
        try:
            info = json.loads(info)
            post = info["posts"][0]
            tags = info["tags"]
        except json.decoder.JSONDecodeError as err:
            logger.error(err)
        return post, tags

    async def getCollection(self, parent_id: int):
        url = "https://" + self.url + "/post?tags=parent:" + str(parent_id)
        async with Request() as request:
            async with request.get(url) as response:
                try:
                    response.raise_for_status()
                except ClientResponseError as err:
                    raise NazurinError(err) from None
                response = await response.text()

        # parse tags in Post.register_tags block
        tag_re = r"Post.register_tags\(\{([\s\S]+?)\}\)"
        tag_ma = re.search(tag_re, response, re.MULTILINE)
        if tag_ma:
            tags = "{" + tag_ma.group(1) + "}"
            try:
                tags = json.loads(tags)
            except json.decoder.JSONDecodeError as err:
                logger.error(err)

        # parse post data in Post.register blocks
        post_re = r"Post.register\(\{([\s\S]+?)\}\)"
        post_ma = re.finditer(post_re, response, re.MULTILINE)
        if not post_ma:
            raise NazurinError("No post find in parent collection")
        posts = []
        for i, match in enumerate(post_ma, start=1):
            post = "{" + match.group(1) + "}"
            try:
                post = json.loads(post)
                if post["has_children"]:
                    posts.insert(0, post)
                else:
                    posts.append(post)
            except json.decoder.JSONDecodeError as err:
                logger.error(err)

        return posts, tags

    async def view(self, post_id: int) -> Illust:
        post, tags = await self.getPost(post_id)
        parent_id = post["parent_id"]
        if not parent_id and post["has_children"]:
            parent_id = post_id
        if parent_id:
            posts, tags = await self.getCollection(parent_id)
        else:
            posts = [post]
        imgs = self.getImages(posts)
        caption = self.buildCaption(posts, tags)
        metadata = {"url": caption["url"], "tags": tags, "posts": posts}
        return Illust(imgs, caption, metadata)

    def pool(self, pool_id: int, jpeg=False):
        client = moebooru(self.site)
        info = client.pool_posts(id=pool_id)
        posts = info["posts"]
        imgs = list()
        for post in posts:
            if not jpeg:
                url = post["file_url"]
            else:
                url = post["jpeg_url"]
            name, _ = self.parseUrl(url)
            imgs.append(Image(name, url))
        caption = Caption({"name": info["name"], "description": info["description"]})
        return imgs, caption

    async def download_pool(self, pool_id, jpeg=False):
        imgs, caption = self.pool(pool_id, jpeg)
        pool_name = caption["name"]
        ensureExistence(os.path.join(TEMP_DIR, pool_name))
        for key, img in enumerate(imgs):
            filename = str(key + 1)
            filename = "0" * (3 - len(filename)) + filename
            _, ext = self.parseUrl(img.url)
            filename += ext
            img.name = pool_name + "/" + img.name
            await img.download()  # TODO

    def getImages(self, posts) -> List[Image]:
        imgs = []
        for i in range(len(posts)):
            post = posts[i]
            file_url = post["file_url"]
            name = unquote(os.path.basename(file_url))
            imgs.append(
                Image(
                    name,
                    file_url,
                    post["sample_url"],
                    post["file_size"],
                    post["width"],
                    post["height"],
                )
            )
        return imgs

    def buildCaption(self, posts, tags) -> Caption:
        """Build media caption from an post."""
        post = posts[0]
        parent_id = post["parent_id"]
        has_children = post["has_children"]
        if has_children:
            url = f"https://{self.url}/post?tags=parent:{str(post['id'])}"
            parent_id = post["id"]
        else:
            url = f"https://{self.url}/post/show/{str(post['id'])}"
        title = post["tags"]
        tag_string = artists = str()
        for tag, tag_type in tags.items():
            if tag_type == "artist":
                artists += tag + " "
            else:
                tag_string += "#" + tag + " "
        source = " ".join(list(set([p["source"] for p in posts]))).strip()
        caption = Caption(
            {
                "title": title,
                "artists": artists,
                "url": url,
                "tags": tag_string,
                "source": source,
                "parent_id": parent_id,
            }
        )
        return caption

    def parseUrl(self, url: str) -> str:
        name = os.path.basename(url)
        return os.path.splitext(name)
