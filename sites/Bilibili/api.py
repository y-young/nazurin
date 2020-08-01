import requests
import shutil
import json
import os
from config import DOWNLOAD_DIR

class Bilibili(object):
    def download(self, id):
        api = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id=' + str(id)
        source = requests.get(api).text
        source = json.loads(source)
        card = json.loads(source['data']['card']['card'])
        pics = card['item']['pictures']
        imgs = list()
        for index, pic in enumerate(pics):
            url = pic['img_src']
            basename = os.path.basename(url)
            extension = os.path.splitext(basename)[1]
            imgs.append({'name': str(id) + '_' + str(index) + extension, 'url': url})

        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        for img in imgs:
            if not os.path.exists(DOWNLOAD_DIR + img['name']):
                response = requests.get(img['url'], stream=True).raw
                with open(DOWNLOAD_DIR + img['name'], 'wb') as f:
                    shutil.copyfileobj(response, f)
        return imgs
