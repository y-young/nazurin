import json
import os
import random
import shlex
import shutil
import subprocess
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Tuple

import aiofiles
import aiofiles.os
from pixivpy3 import AppPixivAPI, PixivError

from nazurin.config import NAZURIN_DATA
from nazurin.database import Database
from nazurin.models import Caption, File, Illust, Ugoira
from nazurin.utils import Request, logger
from nazurin.utils.decorators import async_wrap
from nazurin.utils.exceptions import NazurinError

from .config import (
    DESTINATION,
    DOCUMENT,
    FILENAME,
    HEADERS,
    REFRESH_TOKEN,
    TRANSLATION,
    PixivPrivacy,
)
from .models import PixivIllust, PixivImage

SANITY_LEVEL_LIMITED = "https://s.pximg.net/common/images/limit_sanity_level_360.png"
TOKEN_EXPIRATION_SECONDS = 3600


class Pixiv:
    api = AppPixivAPI()
    db = Database().driver()
    collection = db.collection(NAZURIN_DATA)
    document = collection.document(DOCUMENT)
    updated_time = 0

    illust_detail = async_wrap(api.illust_detail)
    ugoira_metadata = async_wrap(api.ugoira_metadata)
    illust_bookmark_add = async_wrap(api.illust_bookmark_add)
    user_follow_add = async_wrap(api.user_follow_add)
    api_auth = async_wrap(api.auth)

    def __init__(self):
        if TRANSLATION:
            Pixiv.api.set_accept_language(TRANSLATION)

    async def require_auth(self):
        if (
            Pixiv.api.access_token
            and time.time() - Pixiv.updated_time < TOKEN_EXPIRATION_SECONDS
        ):
            # Logged in, access_token not expired
            return
        if Pixiv.api.refresh_token:
            # Logged in, access_token expired
            await self.refresh_token()
            return

        # Haven't logged in
        tokens = await Pixiv.document.get()
        if tokens:
            Pixiv.api.access_token = tokens["access_token"]
            Pixiv.api.refresh_token = tokens["refresh_token"]
            Pixiv.updated_time = tokens["updated_time"]
            if (
                time.time() - Pixiv.updated_time >= TOKEN_EXPIRATION_SECONDS
            ):  # Token expired
                await self.refresh_token()
            else:
                logger.info("Pixiv logged in through cached tokens")
        else:  # Initialize database
            if not REFRESH_TOKEN:
                raise NazurinError("Pixiv refresh token is required")
            Pixiv.api.refresh_token = REFRESH_TOKEN
            await self.auth()
            Pixiv.updated_time = time.time()
            await Pixiv.collection.insert(
                DOCUMENT,
                {
                    "access_token": Pixiv.api.access_token,
                    "refresh_token": Pixiv.api.refresh_token,
                    "updated_time": Pixiv.updated_time,
                },
            )
            logger.info("Pixiv tokens cached")

    async def get_artwork(self, artwork_id: int):
        """Fetch an artwork."""
        response = await self.call(Pixiv.illust_detail, artwork_id)
        if "illust" in response:
            illust = response.illust
        else:
            error = response.error
            msg = error.user_message or error.message
            raise NazurinError(msg)
        if illust.restrict != 0:
            raise NazurinError("Artwork is private")
        return illust

    async def view(self, artwork_id: int) -> Illust:
        illust = await self.get_artwork(artwork_id)
        if illust.type == "ugoira":
            illust = await self.view_ugoira(illust)
        else:  # Ordinary illust
            illust = await self.view_illust(illust)
        return illust

    async def view_illust(self, illust) -> PixivIllust:
        caption = self.build_caption(illust)
        imgs = self.get_images(illust)
        return PixivIllust(illust.id, imgs, caption, illust)

    async def view_ugoira(self, illust) -> Ugoira:
        """Download ugoira zip file, store animation data and convert ugoira to mp4."""
        metadata = await Pixiv.ugoira_metadata(illust.id)
        frames = metadata.ugoira_metadata
        url = illust.meta_single_page.original_image_url
        zip_url = url.replace("/img-original/", "/img-zip-ugoira/")
        zip_url = zip_url.split("_ugoira0")[0] + "_ugoira1920x1080.zip"
        filename = str(illust.id) + "_ugoira1920x1080.zip"
        metafile = File(str(illust.id) + "_ugoira.json", None, DESTINATION)
        gif_zip = File(filename, zip_url, DESTINATION)
        files = [gif_zip, metafile]
        async with Request(headers=HEADERS) as session:
            await gif_zip.download(session)
        async with aiofiles.open(metafile.path, "w") as f:
            await f.write(json.dumps(frames))
        video = await self.ugoira_to_mp4(gif_zip, frames)
        caption = self.build_caption(illust)
        return Ugoira(illust.id, video, caption, illust, files)

    async def bookmark(
        self,
        artwork_id: int,
        privacy: PixivPrivacy = PixivPrivacy.PUBLIC,
    ):
        response = await self.call(Pixiv.illust_bookmark_add, artwork_id, privacy.value)
        if "error" in response:
            logger.error(response)
            raise NazurinError(response.error.user_message or response.error.message)
        logger.info("Bookmarked artwork {}, privacy = {}", artwork_id, privacy.value)
        return True

    async def follow_user(self, user_id: int):
        await self.call(Pixiv.user_follow_add, user_id)

    async def refresh_token(self):
        """Refresh tokens and cache in database."""
        await self.auth()
        Pixiv.updated_time = time.time()
        await Pixiv.document.update(
            {
                "access_token": Pixiv.api.access_token,
                "refresh_token": Pixiv.api.refresh_token,
                "updated_time": Pixiv.updated_time,
            },
        )
        logger.info("Pixiv tokens updated")

    async def call(self, func: Callable, *args):
        """Call API with login state check."""
        await self.require_auth()
        response = await func(*args)
        if (
            "error" in response and "invalid_grant" in response.error.message
        ):  # Access token expired
            await self.refresh_token()
            response = await func(*args)
        return response

    async def ugoira_to_mp4(self, ugoira_zip: File, ugoira_metadata: dict) -> File:
        @async_wrap
        def extract_zip(ugoira_zip: File, to_path: str):
            with zipfile.ZipFile(ugoira_zip.path, "r") as zip_file:
                zip_file.extractall(to_path)

        @async_wrap
        def convert(config: File, output: File):
            # FFmpeg only recognizes POSIX path
            config_path = Path(config.path).as_posix()
            # For some illustrations like https://www.pixiv.net/artworks/44298467,
            # the output video is in YUV444P colorspace,
            # which can't be played on some devices,
            # thus we convert to YUV420P colorspace for better compatibility.
            args = [
                "ffmpeg",
                "-i",
                config_path,
                "-vcodec",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-vf",
                "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                "-y",
                output.path,
            ]
            cmd = shlex.join(args)
            logger.info("Calling FFmpeg with command: {}", cmd)
            try:
                output = subprocess.check_output(
                    args,
                    stderr=subprocess.STDOUT,
                    shell=False,
                )
            except subprocess.CalledProcessError as error:
                logger.error(
                    "FFmpeg failed with code {}, output:\n {}",
                    error.returncode,
                    error.output.decode(),
                )
                raise NazurinError("Failed to convert ugoira to mp4.") from None

        folder = ugoira_zip.name[:-4]
        output_mp4 = File(folder + ".mp4", None, DESTINATION)
        if await output_mp4.exists():
            return output_mp4

        ffconcat = "ffconcat version 1.0\n"
        # no need to specify duration for the last frame
        for frame in ugoira_metadata.frames[:-1]:
            # FFmpeg only recognizes POSIX path
            frame.file = Path(folder, frame.file).as_posix()
            ffconcat += "file " + frame.file + "\n"
            ffconcat += "duration " + str(float(frame.delay) / 1000) + "\n"
        ffconcat += (
            "file " + Path(folder, ugoira_metadata.frames[-1].file).as_posix() + "\n"
        )
        input_config = File(folder + ".ffconcat")
        async with aiofiles.open(input_config.path, "w") as f:
            await f.write(ffconcat)

        zip_path = ugoira_zip.path[:-4]
        await extract_zip(ugoira_zip, zip_path)
        await convert(input_config, output_mp4)

        await async_wrap(shutil.rmtree)(zip_path)
        await aiofiles.os.remove(input_config.path)
        return output_mp4

    def get_images(self, illust) -> List[PixivImage]:
        """Get images from an artwork."""
        width = illust.width
        height = illust.height
        imgs = []
        if illust.meta_pages:  # Contains more than one image
            pages = illust.meta_pages
            for idx, page in enumerate(pages):
                url = page.image_urls.original
                destination, filename = self.get_storage_dest(url, illust, idx)
                imgs.append(
                    PixivImage(
                        filename,
                        url,
                        destination,
                        thumbnail=self.get_thumbnail(url),
                        width=width,
                        height=height,
                    ),
                )
                # For multi-page illusts,
                # width & height will be the size of the first page,
                # we shouldn't guess the sizes of images after
                width = height = 0
        else:
            url = illust.meta_single_page.original_image_url
            if url == SANITY_LEVEL_LIMITED:
                logger.warning(
                    "Artwork {} is not available due to sanity level limit: {}",
                    illust.id,
                    illust,
                )
                raise NazurinError("Artwork not available due to sanity level limit.")
            destination, filename = self.get_storage_dest(url, illust)
            imgs.append(
                PixivImage(
                    filename,
                    url,
                    destination,
                    thumbnail=self.get_thumbnail(url),
                    width=width,
                    height=height,
                ),
            )
        return imgs

    @staticmethod
    def build_caption(illust) -> Caption:
        """Build media caption from an artwork."""
        tags = ""
        for tag in illust.tags:
            if TRANSLATION and tag.translated_name:
                tag_name = tag.translated_name
            else:
                tag_name = tag.name
            tags += "#" + tag_name.replace(" ", "_") + " "
        caption = Caption(
            {
                "title": illust.title,
                "author": "#" + illust.user.name,
                "tags": tags,
                "total_bookmarks": illust.total_bookmarks,
                "url": "pixiv.net/i/" + str(illust.id),
                "bookmarked": illust.is_bookmarked,
            },
        )
        return caption

    @staticmethod
    def get_storage_dest(url: str, illust: dict, page: int = 0) -> Tuple[str, str]:
        """
        Format destination and filename.
        """

        basename = os.path.basename(url)
        filename, extension = os.path.splitext(basename)
        # Convert string to datetime object so that we can use custom fomatting
        # https://docs.python.org/3/library/string.html#format-string-syntax
        create_date = datetime.fromisoformat(illust["create_date"])
        context = {
            # Original filename e.g. 12345678_p0
            "filename": filename,
            "page": page,
            **illust,
            "create_date": create_date,
            "extension": extension,
        }
        return (
            DESTINATION.format_map(context),
            FILENAME.format_map(context) + extension,
        )

    @staticmethod
    def get_thumbnail(url: str) -> str:
        pre, _ = os.path.splitext(url)
        pre = pre.replace("img-original", "img-master")
        thumbnail = pre + "_master1200.jpg"
        return thumbnail

    async def auth(self, *, retry=True):
        try:
            await Pixiv.api_auth()
            if not retry:
                # Reset UA after bypassing successfully
                Pixiv.api.additional_headers = {}
        except PixivError as error:
            if (
                "challenge_basic_security" in error.reason
                or "Captcha challenge" in error.reason
            ):
                # Blocked by CloudFlare, try to bypass by changing UA
                if retry:
                    random_ua = f"PixivAndroidApp/6.{random.randrange(0, 60)}.0"
                    logger.info(
                        "Blocked by CloudFlare, retry with random UA: {}",
                        random_ua,
                    )
                    Pixiv.api.additional_headers = {"User-Agent": random_ua}
                    return await self.auth(retry=False)
                logger.error(error)
                raise NazurinError(
                    "Blocked by CloudFlare security check, please try again later.",
                ) from None
            raise error
