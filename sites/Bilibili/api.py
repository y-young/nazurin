import requests
import json
import os
from utils import downloadImages

class Bilibili(object):
    def fetch(self, dynamic_id):
        """Fetch images and detail."""
        api = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id=' + str(dynamic_id)
        source = requests.get(api).json()
        card = json.loads(source['data']['card']['card'])
        pics = card['item']['pictures']
        imgs = list()
        for index, pic in enumerate(pics):
            url = pic['img_src']
            basename = os.path.basename(url)
            extension = os.path.splitext(basename)[1]
            imgs.append({'name': str(dynamic_id) + '_' + str(index) + extension, 'url': url})

        downloadImages(imgs)
        return imgs, card
