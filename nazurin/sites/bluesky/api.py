import os
from mimetypes import guess_extension
from urllib.parse import urlparse

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import fromisoformat

from .config import DESTINATION, FILENAME


class Bluesky:
    @network_retry
    async def resolve_handle(self, handle: str):
        """
        Get the DID from handle.
        https://endpoints.bsky.app/#bluesky-app/tag/comatprotoidentity/GET/xrpc/com.atproto.identity.resolveHandle
        """
        api = "https://public.api.bsky.app/xrpc/com.atproto.identity.resolveHandle"
        async with (
            Request() as request,
            request.get(
                api,
                params={"handle": handle},
            ) as response,
        ):
            data = await response.json()
            if "error" in data:
                raise NazurinError(data["message"])
            response.raise_for_status()
            return data["did"]

    @network_retry
    async def get_post_thread(self, uri: str, depth: int, parent_height: int):
        """
        Get posts in a thread.
        https://endpoints.bsky.app/#bluesky-app/tag/appbskyfeed/GET/xrpc/app.bsky.feed.getPostThread
        """
        api = "https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread"
        params = {"uri": uri, "depth": depth, "parentHeight": parent_height}
        async with Request() as request, request.get(api, params=params) as response:
            data = await response.json()
            if "error" in data:
                raise NazurinError(data["message"])
            response.raise_for_status()
            return data["thread"]["post"]

    async def fetch(self, user_handle: str, post_rkey: str) -> Illust:
        """Fetch images and detail."""
        user_did = await self.resolve_handle(user_handle)
        post_uri = self.construct_at_uri(user_did, "app.bsky.feed.post", post_rkey)
        item = await self.get_post_thread(post_uri, 0, 0)
        imgs = self.get_images(item)
        caption = self.build_caption(item)
        caption["url"] = f"https://bsky.app/profile/{user_handle}/post/{post_rkey}"
        illust_id = "_".join([user_handle, post_rkey])
        return Illust(illust_id, imgs, caption, item)

    @staticmethod
    def construct_at_uri(authority: str, collection: str, rkey: str):
        """
        Construct at:// URI.
        https://atproto.com/specs/at-uri-scheme
        """
        return f"at://{authority}/{collection}/{rkey}"

    @staticmethod
    def get_images(item: dict) -> list[Image]:
        """Get all images in a post."""
        embed_images = item["embed"]["images"]
        if not embed_images or len(embed_images) == 0:
            raise NazurinError("No image found")
        image_mimetypes = Bluesky.build_mimetypes_map(item)
        imgs = []
        for index, pic in enumerate(embed_images):
            url = pic["fullsize"]
            thumbnail = pic["thumb"]
            destination, filename = Bluesky.get_storage_dest(
                item,
                pic,
                image_mimetypes,
                index,
            )
            imgs.append(
                Image(
                    filename,
                    url,
                    destination,
                    thumbnail,
                ),
            )
        return imgs

    @staticmethod
    def build_mimetypes_map(item: dict) -> dict[str, str]:
        """Map record image blob IDs to MIME types."""
        try:
            return {
                image["image"]["ref"]["$link"]: image["image"]["mimeType"]
                for image in item["record"]["embed"]["images"]
            }
        except (KeyError, TypeError) as error:
            raise NazurinError("Invalid image MIME type metadata") from error

    @staticmethod
    def get_storage_dest(
        item: dict,
        pic: dict,
        image_mimetypes: dict[str, str],
        index: int = 0,
    ) -> tuple[str, str]:
        """
        Format destination and filename.
        """

        url = pic["fullsize"]
        created_at = fromisoformat(item["record"]["createdAt"])
        basename = os.path.basename(urlparse(url).path)
        try:
            mimetype = image_mimetypes[basename]
        except KeyError as error:
            raise NazurinError(
                f"No image MIME type found for blob: {basename}",
            ) from error
        extension = guess_extension(mimetype)
        if extension is None:
            raise NazurinError(f"Unsupported image MIME type: {mimetype}")
        extension = extension.lstrip(".")
        filename = basename
        context = {
            "rkey": item["uri"].split("/")[-1],
            "uri": item["uri"],
            "cid": item["cid"],
            "user": {
                "did": item["author"]["did"],
                "handle": item["author"]["handle"],
                "display_name": item["author"]["displayName"],
            },
            # Original filename, without extension
            "filename": filename,
            # Image index
            "index": index,
            "timestamp": created_at,
            "extension": extension,
            "reply_count": item["replyCount"],
            "repost_count": item["repostCount"],
            "like_count": item["likeCount"],
            "pic": pic,
        }
        return (
            DESTINATION.format_map(context),
            FILENAME.format_map(context) + "." + extension,
        )

    @staticmethod
    def build_caption(item: dict) -> Caption:
        return Caption(
            {
                "author": "#" + item["author"]["displayName"],
                "text": item["record"]["text"],
            },
        )
