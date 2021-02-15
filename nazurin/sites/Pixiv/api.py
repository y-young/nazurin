# -*- coding: utf-8 -*-
import json
import os
import time
from typing import Callable, List, Optional

import aiofiles
from pixivpy3 import AppPixivAPI, PixivError

from nazurin.config import NAZURIN_DATA, TEMP_DIR
from nazurin.database import Database
from nazurin.models import Caption, File
from nazurin.utils import logger
from nazurin.utils.decorators import async_wrap
from nazurin.utils.exceptions import NazurinError

from .config import DOCUMENT, PASSWORD, TRANSLATION, USER
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
    api_login = async_wrap(api.login)
    api_auth = async_wrap(api.auth)

    def __init__(self):
        if TRANSLATION:
            Pixiv.api.set_accept_language(TRANSLATION)

    async def login(self, refresh=False):
        if not refresh:
            tokens = await Pixiv.document.get()
            if tokens:
                Pixiv.api.refresh_token = tokens['refresh_token']
                Pixiv.updated_time = tokens['updated_time']
            else:  # Initialize database
                await self._login()
                return
        if refresh or time.time(
        ) - Pixiv.updated_time >= 3600:  # Access token expired
            await self._refreshToken()
            await Pixiv.document.update({
                'access_token': Pixiv.api.access_token,
                'updated_time': Pixiv.updated_time
            })
            logger.info('Pixiv tokens cached')
        else:
            Pixiv.api.access_token = tokens['access_token']
            logger.info('Pixiv logged in through cached tokens')

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

    async def view_illust(self,
                          artwork_id: Optional[int] = None,
                          illust=None) -> PixivIllust:
        if artwork_id:
            illust = await self.getArtwork(artwork_id)
        if illust.type == 'ugoira':
            raise NazurinError('Ugoira view is not supported.')
        caption = self.buildCaption(illust)
        imgs = self.getImages(illust)
        return PixivIllust(imgs, caption, illust)

    async def download_ugoira(self, illust) -> PixivIllust:
        """Download ugoira zip file and store animation data."""
        metadata = await Pixiv.ugoira_metadata(illust.id)
        metadata = json.dumps(metadata.ugoira_metadata)
        url = illust.meta_single_page.original_image_url
        zip_url = url.replace('/img-original/', '/img-zip-ugoira/')
        zip_url = zip_url.split('_ugoira0')[0] + '_ugoira1920x1080.zip'
        filename = str(illust.id) + '_ugoira1920x1080.zip'
        metafile = str(illust.id) + '_ugoira.json'
        gif_zip = File(filename, zip_url)
        files = [gif_zip, File(metafile)]
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        async with aiofiles.open(os.path.join(TEMP_DIR, metafile), 'w') as f:
            await f.write(metadata)
        return PixivIllust(files=files)

    async def bookmark(self, artwork_id: int):
        response = await self.call(Pixiv.illust_bookmark_add, artwork_id)
        if 'error' in response.keys():
            logger.error(response)
            raise NazurinError(response['error']['user_message'])
        else:
            logger.info('Bookmarked artwork %s', artwork_id)
            return True

    async def _login(self):
        await Pixiv.api_login(USER, PASSWORD)
        Pixiv.updated_time = time.time()
        await Pixiv.collection.insert(
            DOCUMENT, {
                'access_token': Pixiv.api.access_token,
                'refresh_token': Pixiv.api.refresh_token,
                'updated_time': Pixiv.updated_time
            })
        logger.info('Pixiv logged in with password')

    async def _refreshToken(self):
        try:
            await Pixiv.api_auth()
            Pixiv.updated_time = time.time()
            logger.info('Pixiv access token updated')
        except PixivError:  # Refresh token may be expired, try to login with password
            await Pixiv.document.delete()
            await self._login()

    async def call(self, func: Callable, *args):
        """Call API with login state check."""
        if not Pixiv.api.access_token or not Pixiv.api.refresh_token:
            await self.login()
        response = await func(*args)
        if 'error' in response.keys(
        ) and 'invalid_grant' in response.error.message:  # Access token expired
            await self.login(refresh=True)
            response = await func(*args)
        return response

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
