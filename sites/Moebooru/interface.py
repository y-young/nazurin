from database import Database
from time import time
from .api import Moebooru
from .config import COLLECTIONS

patterns = [
    # https://yande.re/post/show/123456
    r'(yande\.re)/post/show/(\d+)',

    # https://files.yande.re/image/1234567890abcdef1234567890abcdef/yande.re%20123456%20aaa-bbb%20ccc_ddd%20ddd%20eee.jpg
    r'(?:[^.]+\.)?(yande\.re)/(?:image|jpeg|sample)/[a-f0-9]{32}/yande\.re%20(\d+)',

    # https://konachan.com/post/show/123456
    r'(konachan\.com)/post/show/(\d+)',

    # https://konachan.com/image/1234567890abcdef1234567890abcdef/Konachan.com%20-%20123456%20aaa-bbb%20ccc_ddd%20ddd%20eee.jpg
    r'(?:[^.]+\.)?(konachan\.com)/(?:image|jpeg|sample)/[a-f0-9]{32}/Konachan\.com%20-%20(\d+)',

    # https://lolibooru.moe/post/show/123456
    r'(lolibooru\.moe)/post/show/(\d+)',

    # https://lolibooru.moe/image/1234567890abcdef1234567890abcdef/lolibooru%20123456%20aaa-bbb%20ccc_ddd%20ddd%20eee.jpg
    r'(lolibooru\.moe)/(?:image|jpeg|sample)/[a-f0-9]{32}/lolibooru%20(\d+)'
]

def handle(match, **kwargs):
    site_url = match.group(1)
    post_id = match.group(2)
    db = Database().driver()
    collection = db.collection(COLLECTIONS[site_url])
    api = Moebooru().site(site_url)

    post, _ = api.getPost(post_id)
    imgs = api.download(post=post)
    post['collected_at'] = time()
    collection.insert(int(post_id), post)
    return imgs