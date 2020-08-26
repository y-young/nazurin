import requests
from utils import NazurinError, downloadImages

class Gelbooru(object):
    def getPost(self, post_id):
        """Fetch an post."""
        api = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id=' + str(post_id)
        response = requests.get(api)
        if not response.text:
            raise NazurinError('Post not found')
        post = response.json()[0]
        return post

    def fetch(self, post_id):
        post = self.getPost(post_id)
        imgs = self.getImages(post)
        downloadImages(imgs)
        return imgs, post

    def getImages(self, post):
        """Get images from post."""
        url = post['file_url']
        filename = 'gelbooru - ' + post['image']
        imgs = list()
        imgs.append({'url': url, 'name': filename})
        return imgs