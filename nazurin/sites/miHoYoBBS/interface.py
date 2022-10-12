from time import time

from nazurin.database import Database
from nazurin.models import Illust

from .api import miHoYoBBS
from .config import COLLECTION

patterns = [
    # https://m.bbs.mihoyo.com/ys?channel=appstore/#/article/30000282
    r'm\.bbs\.mihoyo\.com/[^.]+/#/article/(\d+)',

    # https://bbs.mihoyo.com/ys/article/30000282
    r'bbs\.mihoyo\.com/[0-9a-zA-Z]+/article/(\d+)'
]

async def handle(match, **kwargs) -> Illust:
    post_id = match.group(1)
    db = Database().driver()
    collection = db.collection(COLLECTION)

    illust = await miHoYoBBS().fetch(post_id)
    illust.metadata['collected_at'] = time()
    await collection.insert(post_id, illust.metadata)
    return illust