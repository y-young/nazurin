# -*- coding: utf-8 -*-
import re
import os
from config import *
from pixivpy3 import *
from telegram.ext import run_async

class Pixiv(object):
    api = AppPixivAPI()

    def login(self):
        self.api.login(PIXIV_USER, PIXIV_PASS)
        logger.info('Pixiv logged in successfully')

    def getFilename(self,url, illust):
        basename = os.path.basename(url)
        filename, extension = os.path.splitext(basename)
        name = "%s - %s - %s(%d)%s" % (filename, illust.title, illust.user.name, illust.user.id, extension)
        return self._normalize(name)

    def view(self, id, is_admin=False):
        try:
            illust = self.api.illust_detail(id).illust
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
        response = self.api.illust_bookmark_add(id)
        if 'error' in response.keys():
            logger.error(response)
            raise PixivError(response['error']['user_message'])
        else:
            logger.info('Bookmarked artwork ' + str(id))
            return True

    def _normalize(self, name):
        name = re.sub('[\\\/]', '_', name) # replace / and \
        return name