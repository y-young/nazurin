from time import time

from nazurin.database import Database
from nazurin.models import Illust

from .api import Lofter
from .config import COLLECTION

patterns = [
    # https://username.lofter.com/post/1a2b3c4d_1a2b3c4d5
    r'(\w+)\.lofter\.com/post/(\w+)'
]

async def handle(match) -> Illust:
    username = match.group(1)
    permalink = match.group(2)
    db = Database().driver()
    collection = db.collection(COLLECTION)

    post = await Lofter().fetch(username, permalink)
    post.metadata['collected_at'] = time()
    await collection.insert(int(post.metadata['id']), post.metadata)
    return post
