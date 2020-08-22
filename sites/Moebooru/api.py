from urllib.parse import unquote
import requests
from requests.exceptions import HTTPError
import json
import os
from config import DOWNLOAD_DIR
from utils import NazurinError, downloadImage, downloadImages, logger, sanitizeFilename
from pybooru import Moebooru as moebooru
from bs4 import BeautifulSoup

class Moebooru(object):
    def site(self, site_url='yande.re'):
        self.url = site_url
        return self

    def getPost(self, post_id):
        url = 'https://'+ self.url + '/post/show/' + str(post_id)
        response = requests.get(url)
        try:
            response.raise_for_status()
        except HTTPError as err:
            raise NazurinError(err)

        response = response.text
        soup = BeautifulSoup(response, 'html.parser')
        tag = soup.find(id="post-view").find(recursive=False)
        if tag.name == 'script':
            content = str.strip(tag.string)
        elif tag.name == 'div' and ('status-notice' in tag['class']):
            raise NazurinError(tag.get_text(strip=True))
        else:
            logger.error(tag)
            raise NazurinError('Unknown error')

        info = content[19:-2]
        try:
            info = json.loads(info)
            post = info['posts'][0]
            tags = info['tags']
        except json.decoder.JSONDecodeError as err:
            logger.error(err)
        return post, tags

    def view(self, post_id):
        post, tags = self.getPost(post_id)
        imgs = self.getImages(post)
        caption = self.buildCaption(post, tags)
        return imgs, caption

    def download(self, post_id=None, post=None):
        if post:
            imgs = self.getImages(post)
        else:
            imgs, _ = self.view(post_id)
        downloadImages(imgs)
        return imgs

    def pool(self, pool_id, jpeg=False):
        client = moebooru(self.site)
        info = client.pool_posts(id=pool_id)
        posts = info['posts']
        imgs = list()
        for post in posts:
            if not jpeg:
                url = post['file_url']
            else:
                url = post['jpeg_url']
            name, _ = self.parseUrl(url)
            imgs.append({'name': name, 'url': url})
        details = {'name': info['name'], 'description': info['description']}
        return imgs, details

    def download_pool(self, pool_id, jpeg=False):
        imgs, details = self.pool(pool_id, jpeg)
        pool_name = details['name']
        if not os.path.exists(DOWNLOAD_DIR + pool_name):
            os.makedirs(DOWNLOAD_DIR + pool_name)
        for key, img in enumerate(imgs):
            filename = str(key + 1)
            filename = '0' * (3 - len(filename)) + filename
            _, ext = self.parseUrl(img['url'])
            filename += ext
            downloadImage(img['url'], pool_name + '/' + filename)

    def getImages(self, post):
        file_url = post['file_url']
        name = sanitizeFilename(unquote(os.path.basename(file_url)))
        imgs = [{'url': file_url, 'name': name}]
        return imgs

    def buildCaption(self, post, tags):
        """Build media caption from an post."""
        title = post['tags']
        source = post['source']
        tag_string = artists = str()
        for tag, tag_type in tags.items():
            if tag_type == 'artist':
                artists += tag + ' '
            else:
                tag_string += '#' + tag + ' '
        details = dict()
        if title:
            details['title'] = title
        if artists:
            details['artists'] = artists
        if tag_string:
            details['tags'] = tag_string
        details['url'] = 'https://'+ self.url + '/post/show/' + str(post['id'])
        if source:
            details['source'] = source
        if post['parent_id']:
            details['parent_id'] = post['parent_id']
        if post['has_children']:
            details['has_children'] = True
        return details

    def parseUrl(self, url):
        name = os.path.basename(url)
        return os.path.splitext(name)