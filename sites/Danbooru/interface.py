from database import Database
from time import time
from .api import Danbooru
from .config import COLLECTION

patterns = [
    # https://danbooru.donmai.us/posts/123456
    r'(danbooru)\.donmai\.us/posts/(\d+)',

    # https://safebooru.donmai.us/posts/123456
    r'(safebooru)\.donmai\.us/posts/(\d+)'
]

def handle(match, **kwargs):
    site = match.group(1)
    post_id = match.group(2)
    db = Database().driver()
    collection = db.collection(COLLECTION)
    api = Danbooru(site)

    post = api.getPost(post_id)
    imgs = api.download(post=post)
    post['collected_at'] = time()
    collection.insert(post_id, post)
    return imgs