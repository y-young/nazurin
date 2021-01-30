# -*- coding: utf-8 -*-
import json
import os
import time
from typing import Callable, List, Optional

from pixivpy3 import AppPixivAPI, PixivError

from nazurin.config import NAZURIN_DATA, TEMP_DIR
from nazurin.database import Database
from nazurin.utils import NazurinError, downloadImages, logger

from .config import DOCUMENT, PASSWORD, TRANSLATION, USER
from .models import PixivImage


class Pixiv(object):
    api = AppPixivAPI()
    db = Database().driver()
    collection = db.collection(NAZURIN_DATA)
    document = collection.document(DOCUMENT)
    updated_time = 0

    def __init__(self):
        if TRANSLATION:
            Pixiv.api.set_accept_language(TRANSLATION)

    def login(self, refresh=False):
        if not refresh:
            tokens = Pixiv.document.get()
            if tokens:
                Pixiv.api.refresh_token = tokens['refresh_token']
                Pixiv.updated_time = tokens['updated_time']
            else:  # Initialize database
                self._login()
                return
        if refresh or time.time(
        ) - Pixiv.updated_time >= 3600:  # Access token expired
            self._refreshToken()
            Pixiv.document.update({
                'access_token': Pixiv.api.access_token,
                'updated_time': Pixiv.updated_time
            })
            logger.info('Pixiv tokens cached')
        else:
            Pixiv.api.access_token = tokens['access_token']
            logger.info('Pixiv logged in through cached tokens')

    def getArtwork(self, artwork_id: int):
        """Fetch an artwork."""
        response = self.call(Pixiv.api.illust_detail, artwork_id)
        if 'illust' in response.keys():
            illust = response.illust
        else:
            error = response.error
            msg = error.user_message or error.message
            raise NazurinError(msg)
        if illust.restrict != 0:
            raise NazurinError("Artwork is private")
        return illust

    def view_illust(self, artwork_id: int):
        illust = self.getArtwork(artwork_id)
        if illust.type == 'ugoira':
            raise NazurinError('Ugoira view is not supported.')
        details = self.buildCaption(illust)
        imgs = self.getImages(illust)
        return imgs, details

    async def download_illust(self,
                              artwork_id: Optional[int] = None,
                              illust=None) -> List[PixivImage]:
        """Download and return images of an illustration."""
        if not illust:
            imgs, _ = self.view_illust(artwork_id)
        else:
            imgs = self.getImages(illust)
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        await downloadImages(imgs,
                             headers={'Referer': 'https://app-api.pixiv.net/'})
        return imgs

    def download_ugoira(self, illust) -> List[PixivImage]:
        """Download ugoira zip file and store animation data."""
        metadata = json.dumps(
            Pixiv.api.ugoira_metadata(illust.id).ugoira_metadata)
        url = illust.meta_single_page.original_image_url
        zip_url = url.replace('/img-original/', '/img-zip-ugoira/')
        zip_url = zip_url.split('_ugoira0')[0] + '_ugoira1920x1080.zip'
        filename = str(illust.id) + '_ugoira1920x1080.zip'
        metafile = str(illust.id) + '_ugoira.json'
        imgs = [PixivImage(filename, zip_url), PixivImage(metafile)]
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        with open(os.path.join(TEMP_DIR, metafile), 'w') as f:
            f.write(metadata)
        Pixiv.api.download(zip_url, path=TEMP_DIR, name=filename)
        return imgs

    def bookmark(self, artwork_id: int):
        response = self.call(Pixiv.api.illust_bookmark_add, artwork_id)
        if 'error' in response.keys():
            logger.error(response)
            raise NazurinError(response['error']['user_message'])
        else:
            logger.info('Bookmarked artwork ' + str(artwork_id))
            return True

    def _login(self):
        Pixiv.api.login(USER, PASSWORD)
        Pixiv.updated_time = time.time()
        Pixiv.collection.insert(
            DOCUMENT, {
                'access_token': Pixiv.api.access_token,
                'refresh_token': Pixiv.api.refresh_token,
                'updated_time': Pixiv.updated_time
            })
        logger.info('Pixiv logged in with password')

    def _refreshToken(self):
        try:
            Pixiv.api.auth()
            Pixiv.updated_time = time.time()
            logger.info('Pixiv access token updated')
        except PixivError:  # Refresh token may be expired, try to login with password
            Pixiv.document.delete()
            self._login()

    def call(self, func: Callable, *args):
        """Call API with login state check."""
        if not Pixiv.api.access_token or not Pixiv.api.refresh_token:
            self.login()
        response = func(*args)
        if 'error' in response.keys(
        ) and 'invalid_grant' in response.error.message:  # Access token expired
            self.login(refresh=True)
            response = func(*args)
        return response

    def getImages(self, illust) -> List[PixivImage]:
        """Get images from an artwork."""
        imgs = list()
        if illust.meta_pages:  # Contains more than one image
            pages = illust.meta_pages
            for page in pages:
                url = page.image_urls.original
                name = self.getFilename(url, illust)
                imgs.append(PixivImage(name, url, self.getThumbnail(url)))
        else:
            url = illust.meta_single_page.original_image_url
            name = self.getFilename(url, illust)
            imgs.append(PixivImage(name, url, self.getThumbnail(url)))
        return imgs

    def buildCaption(self, illust):
        """Build media caption from an artwork."""
        tags = str()
        for tag in illust.tags:
            if TRANSLATION and tag.translated_name:
                tag_name = tag.translated_name
            else:
                tag_name = tag.name
            tags += '#' + tag_name.replace(' ', '_') + ' '
        details = {
            'title': illust.title,
            'author': illust.user.name,
            'tags': tags,
            'total_bookmarks': illust.total_bookmarks,
            'url': 'pixiv.net/i/' + str(illust.id)
        }
        details['bookmarked'] = illust.is_bookmarked
        return details

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
