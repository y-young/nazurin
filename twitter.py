import requests
import shutil
import re
import os
from bs4 import BeautifulSoup

def twitter_download(url):
    directory = './downloads/'
    source = requests.get(url).raw
    soup = BeautifulSoup(source, 'html.parser')
    imgs = list()
    items = soup.findAll(property='og:image')
    for item in items:
        src = item.get('content')
        src = src[:-6]
        filename = os.path.basename(src)
        imgs.append({'name': filename, 'url': src})
    if not os.path.exists(directory):
        os.makedirs(directory)
    headers = {'Referer': url, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
    for img in imgs:
        response = requests.get(img['url'], headers=headers, stream=True).raw
        with open(directory + 'twitter - ' + img['name'], 'wb') as f:
            shutil.copyfileobj(response, f)
    return imgs
