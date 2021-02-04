from time import time

from nazurin.database import Database

from .api import Danbooru
from .config import COLLECTION

patterns = [
    # https://danbooru.donmai.us/posts/123456
    # https://safebooru.donmai.us/posts/123456
    r'(?:danbooru|safebooru)\.donmai\.us/posts/(?P<id>\d+)',

    # https://cdn.donmai.us/original/12/ab/12ab34cd56ef7890ab12cd34ef567890.png
    r'cdn\.donmai\.us/\w+/(?:[a-f0-9]{2}/){2}(?P<md5>[a-f0-9]{32})'
]

async def handle(match, **kwargs):
    api = Danbooru()
    db = Database().driver()
    collection = db.collection(COLLECTION)

    if match.lastgroup == 'id':
        post_id = match.group(1)
        post = api.getPost(post_id)
    else:
        md5 = match.group(1)
        post = api.getPost(md5=md5)

    imgs = api.download(post=post)
    post['collected_at'] = time()
    await collection.insert(int(post['id']), post)
    return imgs
