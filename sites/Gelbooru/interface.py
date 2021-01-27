from time import time

from database import Database

from .api import Gelbooru
from .config import COLLECTION

patterns = [
    # https://gelbooru.com/index.php?page=post&s=view&id=123456
    r'gelbooru\.com/index\.php\?page=post&s=view&id=(\d+)'
]

def handle(match, **kwargs):
    post_id = match.group(1)
    db = Database().driver()
    collection = db.collection(COLLECTION)

    imgs, post = Gelbooru().fetch(post_id)
    post['collected_at'] = time()
    collection.insert(int(post_id), post)
    return imgs
