import binascii
import json
import os
import re
from datetime import datetime
from http import HTTPStatus
from http.cookies import SimpleCookie
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from nazurin.models import Caption, Illust, Image
from nazurin.models.file import File
from nazurin.utils import Request, logger
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

from .config import DESTINATION, DOWNLOAD_FILENAME, FILENAME

BASE_URL = "https://www.deviantart.com"


class DeviantArt:
    csrf_token: str = None
    cookies: SimpleCookie = None

    @network_retry
    async def get_deviation(self, deviation_id: int, *, retry: bool = False) -> dict:
        """Fetch a deviation."""
        await self.require_csrf_token(refresh=retry)
        api = f"{BASE_URL}/_napi/da-user-profile/shared_api/deviation/extended_fetch"
        params = {
            "type": "art",
            "deviationid": deviation_id,
            "csrf_token": self.csrf_token,
        }
        async with Request(
            cookies=DeviantArt.cookies,
            headers={"Referer": BASE_URL},
        ) as request, request.get(api, params=params) as response:
            if response.status == HTTPStatus.NOT_FOUND:
                raise NazurinError("Deviation not found")
            response.raise_for_status()

            data = await response.json()
            if "error" in data:
                logger.error(data)
                # If CSRF token is invalid, try to get a new one
                if data.get("errorDetails", {}).get("csrf") == "invalid" and not retry:
                    logger.info("CSRF token seems expired, refreshing...")
                    return await self.get_deviation(deviation_id, retry=True)
                raise NazurinError(data["errorDescription"])

            deviation = data["deviation"]
            del deviation["extended"]["relatedContent"]
            return deviation

    async def fetch(self, deviation_id: str) -> Illust:
        deviation = await self.get_deviation(deviation_id)
        imgs = self.get_images(deviation)
        caption = self.build_caption(deviation)
        file = await self.get_download(deviation)
        return Illust(deviation_id, imgs, caption, deviation, [file] if file else [])

    def get_images(self, deviation: dict) -> List[Image]:
        """Get images from deviation."""
        filename, url, thumbnail = self.parse_url(deviation)
        original_file = deviation["extended"]["originalFile"]
        destination, filename = self.get_storage_dest(deviation, filename)
        imgs = [
            Image(
                filename,
                url,
                destination,
                thumbnail,
                original_file["filesize"],
                original_file["width"],
                original_file["height"],
            ),
        ]
        return imgs

    @staticmethod
    def get_storage_dest(
        deviation: dict,
        filename: str,
        *,
        is_download: bool = False,
    ) -> Tuple[str, str]:
        """
        Format destination and filename.

        Download files is distinguished through `is_download`,
        and will be formatted using another template.
        """

        time_string = deviation["publishedTime"]
        # Insert a colon in time offset otherwise datetime won't recognize it
        # e.g. 2009-09-09T06:26:37-0700 -> 2009-09-09T06:26:37-07:00
        time_string = f"{time_string[0:-2]}:{time_string[-2:]}"
        published_time = datetime.fromisoformat(time_string)

        filename, extension = os.path.splitext(filename)
        context = {
            **deviation,
            # Default filename (UUID), without extension
            # For human-friendly name of download file, use `prettyName`
            "filename": filename,
            "publishedTime": published_time,
            "extension": extension,
        }
        filename = (DOWNLOAD_FILENAME if is_download else FILENAME).format_map(context)
        return (DESTINATION.format_map(context), filename + extension)

    async def get_download(self, deviation: dict) -> Optional[File]:
        if not deviation["isDownloadable"]:
            return None
        download = deviation["extended"]["download"]
        original_file = deviation["extended"]["originalFile"]

        if (
            download["width"]
            and download["filesize"] == original_file["filesize"]
            and download["width"] == original_file["width"]
            and download["height"] == original_file["height"]
        ):
            logger.info("No need to download since it's the same as the original image")
            return None

        author_uuid = deviation["author"]["useridUuid"]
        url = urlparse(deviation["media"]["baseUri"])
        filename = os.path.basename(download["url"]).split("?")[0]
        url = url._replace(
            netloc=url.netloc.replace("images-wixmp-", "wixmp-"),
            path=f"/f/{author_uuid}/{filename}",
        )
        token = self.generate_token(url.path)

        # Duplicate attribute on top level for convenience
        deviation["prettyName"] = deviation["media"]["prettyName"]
        destination, filename = self.get_storage_dest(
            deviation,
            filename,
            is_download=True,
        )
        return File(filename, f"{url.geturl()}?token={token}", destination)

    @staticmethod
    def build_caption(deviation: dict) -> Caption:
        caption = Caption(
            {
                "title": deviation["title"],
                "author": f"#{deviation['author']['username']}",
                "url": deviation["url"],
            },
        )
        if "tags" in deviation["extended"]:
            caption["tags"] = " ".join(
                ["#" + tag["name"] for tag in deviation["extended"]["tags"]],
            )
        return caption

    def parse_url(self, deviation: dict) -> Tuple[str, str, str]:
        """
        Get filename, original file url & thumbnail url of deviation.
        """

        media = deviation["media"]
        base_uri = media["baseUri"]
        tokens = media.get("token", [])
        types = {}
        for type_ in media["types"]:
            types[type_["t"]] = type_

        filename = os.path.basename(base_uri)
        path = urlparse(base_uri).path

        token = tokens[0] if len(tokens) > 0 else ""
        if path.startswith("/f/"):
            url = f"{base_uri}?token={self.generate_token(path)}"
            if "fullview" in types:
                thumbnail = types["fullview"]
                # Sometimes fullview has no subpath but there're two tokens,
                # in that case the base_uri should be used along with the second token
                # e.g. https://www.deviantart.com/exitmothership/art/Unfold-879580475
                if "c" not in thumbnail and len(tokens) > 1:
                    thumbnail["c"] = ""
                    token = tokens[1]
            else:
                thumbnail = types["preview"]
            thumbnail = base_uri + thumbnail["c"].replace(
                "<prettyName>",
                media["prettyName"],
            )
            thumbnail = f"{thumbnail}?token={token}"
        elif base_uri.endswith(".gif"):  # TODO: Send GIFs properly
            thumbnail = url = f"{types['gif']['b']}?token={token}"
        else:
            thumbnail = url = base_uri

        return filename, url, thumbnail

    @staticmethod
    def generate_token(path: str) -> str:
        header = "eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0"  # {"typ":"JWT","alg":"none"}
        payload = {
            "sub": "urn:app:",
            "iss": "urn:app:",
            "obj": [[{"path": path}]],
            "aud": ["urn:service:file.download"],
        }
        payload = json.dumps(payload).encode()
        payload = binascii.b2a_base64(payload).rstrip(b"=\n").decode()
        return f"{header}.{payload}."

    @network_retry
    async def require_csrf_token(self, *, refresh: bool = False) -> None:
        if self.csrf_token and not refresh:
            return
        logger.info("Fetching CSRF token...")
        async with Request() as request, request.get(BASE_URL) as response:
            response.raise_for_status()
            pattern = re.compile(r"window\.__CSRF_TOKEN__ = '(\S+)';")
            content = await response.text()
            match = pattern.search(content)
            if not match:
                raise NazurinError("Unable to get CSRF token")
            DeviantArt.csrf_token = match.group(1)
            # CSRF token must be used along with the cookies returned,
            # otherwise will be considered invalid
            DeviantArt.cookies = response.cookies
            logger.info(
                "Fetched CSRF token: {}, cookies: {}",
                DeviantArt.csrf_token,
                DeviantArt.cookies,
            )
