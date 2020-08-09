# -*- coding: utf-8 -*-
import re
import os
import time
from config import NAZURIN_DATA, DOWNLOAD_DIR, logger
from sites.Pixiv.config import PIXIV_DOCUMENT, PIXIV_USER, PIXIV_PASS
from utils import NazurinError
from database import Database
from pixivpy3 import AppPixivAPI, PixivError
from telegram.ext import run_async

class Pixiv(object):
    api = AppPixivAPI()
    db = Database().driver()
    collection = db.collection(NAZURIN_DATA)
    document = collection.document(PIXIV_DOCUMENT)
    updated_time = 0

    def login(self, refresh=False):
        if not refresh:
            tokens = Pixiv.document.get()
            if tokens:
                Pixiv.api.refresh_token = tokens['refresh_token']
                Pixiv.updated_time = tokens['updated_time']
            else: # Initialize database
                self._login()
                return
        if refresh or time.time() - Pixiv.updated_time >= 3600: # Access token expired
            self._refreshToken()
            Pixiv.document.update({
                'access_token': Pixiv.api.access_token,
                'updated_time': Pixiv.updated_time
            })
            logger.info('Pixiv tokens cached')
        else:
            Pixiv.api.access_token = tokens['access_token']
            logger.info('Pixiv logged in through cached tokens')

    def view(self, artwork_id, is_admin=False):
        response = self.call(Pixiv.api.illust_detail, artwork_id)
        if 'illust' in response.keys():
            illust = response.illust
        else:
            raise NazurinError("Artwork not found")
        if illust.restrict != 0:
            raise NazurinError("Artwork not found or is private")

        imgs = list()
        tags = str()
        for tag in illust.tags:
            tags += '#' + tag.name + ' '
        details = {'title': illust.title, 'author': illust.user.name, 'tags': tags, 'total_bookmarks': illust.total_bookmarks, 'url': 'pixiv.net/i/' + str(artwork_id)}
        if is_admin:
            details['bookmarked'] = illust.is_bookmarked
        if illust.meta_pages: # Contains more than one image
            pages = illust.meta_pages
            for page in pages:
                url = page.image_urls.original
                name = self.getFilename(url, illust)
                imgs.append({'url': url, 'name': name})
        else:
            url = illust.meta_single_page.original_image_url
            name = self.getFilename(url, illust)
            imgs.append({'url': url, 'name': name})
        return imgs, details

    def download(self, artwork_id):
        imgs, _ = self.view(artwork_id)
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        for img in imgs:
            filename = DOWNLOAD_DIR + img['name']
            if (not os.path.exists(filename)) or os.stat(filename).st_size == 0:
                Pixiv.api.download(img['url'], path=DOWNLOAD_DIR, name=img['name'])
        return imgs

    @run_async
    def bookmark(self, artwork_id):
        response = self.call(Pixiv.api.illust_bookmark_add, artwork_id)
        if 'error' in response.keys():
            logger.error(response)
            raise NazurinError(response['error']['user_message'])
        else:
            logger.info('Bookmarked artwork ' + str(artwork_id))
            return True

    def _login(self):
        Pixiv.api.login(PIXIV_USER, PIXIV_PASS)
        Pixiv.updated_time = time.time()
        Pixiv.collection.insert(PIXIV_DOCUMENT, {
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
        except PixivError: # Refresh token may be expired, try to login with password
            Pixiv.document.delete()
            self._login()

    def call(self, func, *args):
        if not Pixiv.api.access_token or not Pixiv.api.refresh_token:
            self.login()
        response = func(*args)
        if 'error' in response.keys() and 'invalid_grant' in response.error.message: # Access token expired
            self.login(refresh=True)
            response = func(*args)
        return response

    def getFilename(self,url, illust):
        basename = os.path.basename(url)
        filename, extension = os.path.splitext(basename)
        name = "%s - %s - %s(%d)%s" % (filename, illust.title, illust.user.name, illust.user.id, extension)
        return self._normalize(name)

    def _normalize(self, name):
        name = re.sub('[\\\/]', '_', name) # replace / and \
        return name