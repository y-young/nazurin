from time import time

from nazurin.database import Database

from .api import Zerochan
from .config import COLLECTION

patterns = [
    # https://www.zerochan.net/123456
    r'zerochan\.net/(\d+)',

    # https://s1.zerochan.net/Abcdef.600.123456.jpg
    # https://static.zerochan.net/Abcdef.full.123456.jpg
    r'zerochan\.net/\S+\.(\d+)\.\w+$'
]

async def handle(match, **kwargs):
    post_id = match.group(1)
    api = Zerochan()
    db = Database().driver()
    collection = db.collection(COLLECTION)

    post = await api.getPost(post_id)
    imgs = await api.download(post=post)
    post['collected_at'] = time()
    await collection.insert(int(post_id), post)
    return imgs
