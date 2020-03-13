# -*- coding: utf-8 -*-
import re
import os
import time
from config import *
from database import Firebase
from pixivpy3 import *
from telegram.ext import run_async

class Pixiv(object):
    def __init__(self):
        self.api = AppPixivAPI()
        self.db = Firebase()

    def login(self, refresh=False):
        if not refresh:
            tokens = self.db.get(FIREBASE_COLLECION, 'pixiv')
            if tokens:
                self.api.refresh_token = tokens['refresh_token']
                self.updated_time = tokens['updated_time']
            else: # Initialize database
                self._login()
        if refresh or time.time() - self.updated_time >= 3600: # Access token expired
            self._refreshToken()
            self.db.store(FIREBASE_COLLECION, 'pixiv', {
                'access_token': self.api.access_token,
                'refresh_token': self.api.refresh_token,
                'updated_time': self.updated_time
            })
            logger.info('Pixiv tokens cached')
        else:
            self.api.access_token = tokens['access_token']
            logger.info('Pixiv logged in through cached tokens')

    def view(self, id, is_admin=False):
        try:
            illust = self.call(self.api.illust_detail, id).illust
        except AttributeError:
            raise PixivError("Artwork not found")
        if illust.restrict == 2:
            raise PixivError("Artwork not found or is private")
        imgs = list()
        tags = str()
        for tag in illust.tags:
            tags += '#' + tag.name + ' '
        details = {'title': illust.title, 'author': illust.user.name, 'tags': tags, 'total_bookmarks': illust.total_bookmarks, 'url': 'pixiv.net/i/' + str(id)}
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

    def download(self, id=None, imgs=None):
        if not imgs:
            imgs, _ = self.view(id)
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        for img in imgs:
            if not os.path.exists(DOWNLOAD_DIR + img['name']):
                self.api.download(img['url'], path=DOWNLOAD_DIR, name=img['name'])
        return imgs

    @run_async
    def bookmark(self, id):
        response = self.call(self.api.illust_bookmark_add, id)
        if 'error' in response.keys():
            logger.error(response)
            raise PixivError(response['error']['user_message'])
        else:
            logger.info('Bookmarked artwork ' + str(id))
            return True

    def _login(self):
        self.api.login()
        self.updated_time = time.time()
        logger.info('Pixiv logged in with password')

    def _refreshToken(self):
        try:
            response = self.api.auth()
            self.updated_time = time.time()
            logger.info('Pixiv access token updated')
        except PixivError: # Refresh token may be expired, try to login with password
            self._login()

    def call(self, func, *args):
        if not self.api.access_token or not self.api.refresh_token:
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