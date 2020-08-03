import requests
import shutil
import json
import re
import os
from utils import logger, downloadImages
from config import DOWNLOAD_DIR
from bs4 import BeautifulSoup

class Twitter(object):
    def download(self, id):
        api = 'https://syndication.twitter.com/tweets.json?ids='+ id +'&lang=en'
        source = requests.get(api).text
        source = json.loads(source)[id]
        soup = BeautifulSoup(source, 'html.parser')
        imgs = list()
        items = soup.findAll('img',attrs={'data-image': True})
        for item in items:
            src = item.get('data-image')
            ext = item.get('data-image-format')
            filename, url = self.parseUrl(src, ext)
            imgs.append({'name': 'twitter - '+ filename, 'url': url})
        logger.info(imgs)
        downloadImages(imgs)
        return imgs

    def parseUrl(self, src, extension):
        '''
        Get filename & the url of the original image
        eg:
            url: https://pbs.twimg.com/media/DOhM30VVwAEpIHq
            extension: jpg
            return: DOhM30VVwAEpIHq.jpg, https://pbs.twimg.com/media/DOhM30VVwAEpIHq?format=jpg&name=orig
        Doc: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/entities-object
        '''
        basename = os.path.basename(src)
        filename = basename + '.' + extension
        url = src + '?format=' + extension + '&name=orig'
        return filename, url