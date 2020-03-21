import requests
import shutil
import re
import os
from config import DOWNLOAD_DIR
from bs4 import BeautifulSoup

class Twitter(object):
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
    handlers = []
    def download(self, url):
        # Cannot get image meta from mobile Twitter
        url = url.replace('mobile.twitter.com', 'twitter.com')
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'html.parser')
        imgs = list()
        items = soup.findAll(property='og:image')
        for item in items:
            src = item.get('content')
            filename, url = self.parseUrl(src)
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

    def parseUrl(self, url):
        '''
        Get filename & the url of the original image  
        eg: https://pbs.twimg.com/media/DOhM30VVwAEpIHq?format=jpg&name=orig  
        Doc: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/entities-object
        '''
        src = url[:-6]
        basename = os.path.basename(src)
        filename = os.path.splitext(basename)[0]
        extension = os.path.splitext(basename)[1][1:]
        dirname = os.path.dirname(src)
        src = dirname + '/' + filename + '?format=' + extension + '&name=orig'
        return basename, src