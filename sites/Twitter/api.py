import requests
import shutil
import json
import re
import os
from utils import logger
from config import DOWNLOAD_DIR
from bs4 import BeautifulSoup

class Twitter(object):
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'

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
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        headers = {'Referer': url, 'User-Agent': self.UA}
        for img in imgs:
            if not os.path.exists(DOWNLOAD_DIR + img['name']):
                response = requests.get(img['url'], headers=headers, stream=True).raw
                with open(DOWNLOAD_DIR + img['name'], 'wb') as f:
                    shutil.copyfileobj(response, f)
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