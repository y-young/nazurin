# -*- coding: utf-8 -*-
import json
import os
import time

from pixivpy3 import AppPixivAPI

from config import NAZURIN_DATA, TEMP_DIR
from database import Database
from utils import NazurinError, logger

from .config import DOCUMENT, REFRESH_TOKEN, TRANSLATION
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

    def requireAuth(self):
        if Pixiv.api.access_token and time.time() - Pixiv.updated_time < 3600:
            # Logged in, access_token not expired
            return
        if Pixiv.api.refresh_token:
            # Logged in, access_token expired
            self.refreshToken()
            return

        # Haven't logged in
        tokens = Pixiv.document.get()
        if tokens:
            Pixiv.api.access_token = tokens['access_token']
            Pixiv.api.refresh_token = tokens['refresh_token']
            Pixiv.updated_time = tokens['updated_time']
            if time.time() - Pixiv.updated_time >= 3600:  # Token expired
                self.refreshToken()
            else:
                logger.info('Pixiv logged in through cached tokens')
        else:  # Initialize database
            if not REFRESH_TOKEN:
                raise NazurinError('Pixiv refresh token is required')
            Pixiv.api.refresh_token = REFRESH_TOKEN
            Pixiv.api.auth()
            Pixiv.updated_time = time.time()
            Pixiv.collection.insert(
                DOCUMENT, {
                    'access_token': Pixiv.api.access_token,
                    'refresh_token': Pixiv.api.refresh_token,
                    'updated_time': Pixiv.updated_time
                })
            logger.info('Pixiv tokens cached')

    def getArtwork(self, artwork_id):
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

    def view_illust(self, artwork_id):
        illust = self.getArtwork(artwork_id)
        if illust.type == 'ugoira':
            raise NazurinError('Ugoira view is not supported.')
        details = self.buildCaption(illust)
        imgs = self.getImages(illust)
        return imgs, details

    def download_illust(self, artwork_id=None, illust=None):
        """Download and return images of an illustration."""
        if not illust:
            imgs, _ = self.view_illust(artwork_id)
        else:
            imgs = self.getImages(illust)
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        for img in imgs:
            if (not os.path.exists(img.path)) or os.stat(
                    img.path).st_size == 0:
                Pixiv.api.download(img.url, path=TEMP_DIR, name=img.name)
        return imgs

    def download_ugoira(self, illust):
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

    def bookmark(self, artwork_id):
        response = self.call(Pixiv.api.illust_bookmark_add, artwork_id)
        if 'error' in response.keys():
            logger.error(response)
            raise NazurinError(response['error']['user_message'])
        else:
            logger.info('Bookmarked artwork %s', artwork_id)
            return True

    def refreshToken(self):
        """Refresh tokens and cache in database."""
        Pixiv.api.auth()
        Pixiv.updated_time = time.time()
        Pixiv.document.update({
            'access_token': Pixiv.api.access_token,
            'refresh_token': Pixiv.api.refresh_token,
            'updated_time': Pixiv.updated_time
        })
        logger.info('Pixiv tokens updated')

    def call(self, func, *args):
        """Call API with login state check."""
        self.requireAuth()
        response = func(*args)
        if 'error' in response.keys(
        ) and 'invalid_grant' in response.error.message:  # Access token expired
            self.refreshToken()
            response = func(*args)
        return response

    def getImages(self, illust):
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

    def getFilename(self, url, illust):
        basename = os.path.basename(url)
        filename, extension = os.path.splitext(basename)
        name = "%s - %s - %s(%d)%s" % (filename, illust.title,
                                       illust.user.name, illust.user.id,
                                       extension)
        return name

    def getThumbnail(self, url):
        pre, _ = os.path.splitext(url)
        pre = pre.replace('img-original', 'img-master')
        thumbnail = pre + '_master1200.jpg'
        return thumbnail
