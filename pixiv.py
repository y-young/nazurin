# -*- coding: utf-8 -*-
import os
from pixivpy3 import *

def getFilename(url, illust):
    basename = os.path.basename(url)
    filename = os.path.splitext(basename)[0]
    extension = os.path.splitext(basename)[1]
    name = "%s - %s - %s(%d)%s" % (filename, illust.title, illust.user.name, illust.user.id, extension)
    return name

def artworkDetail(id):
    global api
    illust = api.illust_detail(id).illust
    imgs = list()
    if illust.meta_pages: # Contains more than one image
        pages = illust.meta_pages
        for page in pages:
            url = page.image_urls.original
            name = getFilename(url, illust)
            imgs.append({'url': url, 'name': name})
    else:
        url = illust.meta_single_page.original_image_url
        name = getFilename(url, illust)
        imgs.append({'url': url, 'name': name})
    return imgs

def downloadArtwork(id):
    imgs = artworkDetail(id)
    for img in imgs:
        api.download(img['url'], path='./', name=img['name'])