# -*- coding: utf-8 -*-
import json
import os
import shlex
import shutil
import subprocess
import time
import zipfile
from typing import Callable, List

import aiofiles
import aiofiles.os
from pixivpy3 import AppPixivAPI

from nazurin.config import NAZURIN_DATA
from nazurin.database import Database
from nazurin.models import Caption, File, Illust, Ugoira
from nazurin.utils import Request, logger
from nazurin.utils.decorators import async_wrap
from nazurin.utils.exceptions import NazurinError

from .config import DOCUMENT, HEADERS, REFRESH_TOKEN, TRANSLATION
from .models import PixivIllust, PixivImage

class Pixiv(object):
    api = AppPixivAPI()
    db = Database().driver()
    collection = db.collection(NAZURIN_DATA)
    document = collection.document(DOCUMENT)
    updated_time = 0

    illust_detail = async_wrap(api.illust_detail)
    ugoira_metadata = async_wrap(api.ugoira_metadata)
    illust_bookmark_add = async_wrap(api.illust_bookmark_add)
    api_auth = async_wrap(api.auth)

    def __init__(self):
        if TRANSLATION:
            Pixiv.api.set_accept_language(TRANSLATION)

    async def requireAuth(self):
        if Pixiv.api.access_token and time.time() - Pixiv.updated_time < 3600:
            # Logged in, access_token not expired
            return
        if Pixiv.api.refresh_token:
            # Logged in, access_token expired
            await self.refreshToken()
            return

        # Haven't logged in
        tokens = await Pixiv.document.get()
        if tokens:
            Pixiv.api.access_token = tokens['access_token']
            Pixiv.api.refresh_token = tokens['refresh_token']
            Pixiv.updated_time = tokens['updated_time']
            if time.time() - Pixiv.updated_time >= 3600:  # Token expired
                await self.refreshToken()
            else:
                logger.info('Pixiv logged in through cached tokens')
        else:  # Initialize database
            if not REFRESH_TOKEN:
                raise NazurinError('Pixiv refresh token is required')
            Pixiv.api.refresh_token = REFRESH_TOKEN
            await Pixiv.api_auth()
            Pixiv.updated_time = time.time()
            await Pixiv.collection.insert(
                DOCUMENT, {
                    'access_token': Pixiv.api.access_token,
                    'refresh_token': Pixiv.api.refresh_token,
                    'updated_time': Pixiv.updated_time
                })
            logger.info('Pixiv tokens cached')

    async def getArtwork(self, artwork_id: int):
        """Fetch an artwork."""
        response = await self.call(Pixiv.illust_detail, artwork_id)
        if 'illust' in response.keys():
            illust = response.illust
        else:
            error = response.error
            msg = error.user_message or error.message
            raise NazurinError(msg)
        if illust.restrict != 0:
            raise NazurinError("Artwork is private")
        return illust

    async def view(self, artwork_id: int = None) -> Illust:
        illust = await self.getArtwork(artwork_id)
        if illust.type == 'ugoira':
            illust = await self.viewUgoira(illust)
        else:  # Ordinary illust
            illust = await self.viewIllust(illust)
        return illust

    async def viewIllust(self, illust) -> PixivIllust:
        caption = self.buildCaption(illust)
        imgs = self.getImages(illust)
        return PixivIllust(imgs, caption, illust)

    async def viewUgoira(self, illust) -> Ugoira:
        """Download ugoira zip file, store animation data and convert ugoira to mp4."""
        metadata = await Pixiv.ugoira_metadata(illust.id)
        frames = metadata.ugoira_metadata
        url = illust.meta_single_page.original_image_url
        zip_url = url.replace('/img-original/', '/img-zip-ugoira/')
        zip_url = zip_url.split('_ugoira0')[0] + '_ugoira1920x1080.zip'
        filename = str(illust.id) + '_ugoira1920x1080.zip'
        metafile = File(str(illust.id) + '_ugoira.json')
        gif_zip = File(filename, zip_url)
        files = [gif_zip, metafile]
        async with Request(headers=HEADERS) as session:
            await gif_zip.download(session)
        async with aiofiles.open(metafile.path, 'w') as f:
            await f.write(json.dumps(frames))
        video = await self.ugoira2Mp4(gif_zip, frames)
        caption = self.buildCaption(illust)
        return Ugoira(video, caption, illust, files)

    async def bookmark(self, artwork_id: int):
        response = await self.call(Pixiv.illust_bookmark_add, artwork_id)
        if 'error' in response.keys():
            logger.error(response)
            raise NazurinError(response['error']['user_message'])
        else:
            logger.info('Bookmarked artwork %s', artwork_id)
            return True

    async def refreshToken(self):
        """Refresh tokens and cache in database."""
        await Pixiv.api_auth()
        Pixiv.updated_time = time.time()
        await Pixiv.document.update({
            'access_token': Pixiv.api.access_token,
            'refresh_token': Pixiv.api.refresh_token,
            'updated_time': Pixiv.updated_time
        })
        logger.info('Pixiv tokens updated')

    async def call(self, func: Callable, *args):
        """Call API with login state check."""
        await self.requireAuth()
        response = await func(*args)
        if 'error' in response.keys(
        ) and 'invalid_grant' in response.error.message:  # Access token expired
            await self.refreshToken()
            response = await func(*args)
        return response

    async def ugoira2Mp4(self, ugoira_zip: File,
                         ugoira_metadata: dict) -> File:
        @async_wrap
        def extractUgoiraZip(ugoira_zip: File, to_path: str):
            with zipfile.ZipFile(ugoira_zip.path, 'r') as zip_file:
                zip_file.extractall(to_path)

        @async_wrap
        def convert(config: File, output: File):
            cmd = f'ffmpeg -i {config.path} -vcodec libx264 -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -y {output.path}'
            logger.info('Calling FFmpeg with command: %s', cmd)
            args = shlex.split(cmd)
            try:
                output = subprocess.check_output(args,
                                                 stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as error:
                logger.error('FFmpeg failed with code %s, output:\n %s',
                             error.returncode, error.output)
                raise NazurinError(
                    'Failed to convert ugoira to mp4.') from None

        folder = ugoira_zip.name[:-4]
        output_mp4 = File(folder + '.mp4')
        if await output_mp4.exists():
            return output_mp4

        ffconcat = 'ffconcat version 1.0\n'
        for frame in ugoira_metadata.frames:
            frame.file = folder + '/' + frame.file
            ffconcat += 'file ' + frame.file + '\n'
            ffconcat += 'duration ' + str(float(frame.delay) / 1000) + '\n'
        ffconcat += 'file ' + ugoira_metadata.frames[-1].file + '\n'
        input_config = File(folder + '.ffconcat')
        async with aiofiles.open(input_config.path, 'w') as f:
            await f.write(ffconcat)

        zip_path = ugoira_zip.path[:-4]
        await extractUgoiraZip(ugoira_zip, zip_path)
        await convert(input_config, output_mp4)

        await async_wrap(shutil.rmtree)(zip_path)
        await aiofiles.os.remove(input_config.path)
        return output_mp4

    def getImages(self, illust) -> List[PixivImage]:
        """Get images from an artwork."""
        width = illust.width
        height = illust.height
        imgs = list()
        if illust.meta_pages:  # Contains more than one image
            pages = illust.meta_pages
            for page in pages:
                url = page.image_urls.original
                name = self.getFilename(url, illust)
                # For multi-page illusts, width & height will be the size of the first page
                imgs.append(
                    PixivImage(name,
                               url,
                               self.getThumbnail(url),
                               width=width,
                               height=height))
        else:
            url = illust.meta_single_page.original_image_url
            name = self.getFilename(url, illust)
            imgs.append(
                PixivImage(name,
                           url,
                           self.getThumbnail(url),
                           width=width,
                           height=height))
        return imgs

    def buildCaption(self, illust) -> Caption:
        """Build media caption from an artwork."""
        tags = str()
        for tag in illust.tags:
            if TRANSLATION and tag.translated_name:
                tag_name = tag.translated_name
            else:
                tag_name = tag.name
            tags += '#' + tag_name.replace(' ', '_') + ' '
        caption = Caption({
            'title': illust.title,
            'author': illust.user.name,
            'tags': tags,
            'total_bookmarks': illust.total_bookmarks,
            'url': 'pixiv.net/i/' + str(illust.id),
            'bookmarked': illust.is_bookmarked
        })
        return caption

    def getFilename(self, url: str, illust) -> str:
        basename = os.path.basename(url)
        filename, extension = os.path.splitext(basename)
        name = "%s - %s - %s(%d)%s" % (filename, illust.title,
                                       illust.user.name, illust.user.id,
                                       extension)
        return name

    def getThumbnail(self, url: str) -> str:
        pre, _ = os.path.splitext(url)
        pre = pre.replace('img-original', 'img-master')
        thumbnail = pre + '_master1200.jpg'
        return thumbnail
