from time import time

from nazurin.database import Database

from .api import Gelbooru
from .config import COLLECTION

patterns = [
    # https://gelbooru.com/index.php?page=post&s=view&id=123456
    r'gelbooru\.com/index\.php\?page=post&s=view&id=(\d+)'
]

async def handle(match, **kwargs):
    post_id = match.group(1)
    db = Database().driver()
    collection = db.collection(COLLECTION)

    imgs, post = await Gelbooru().fetch(post_id)
    post['collected_at'] = time()
    await collection.insert(int(post_id), post)
    return imgs
