from time import time

from nazurin.database import Database
from nazurin.models import Illust

from .api import Bilibili
from .config import COLLECTION

patterns = [
    # https://t.bilibili.com/123456789012345678
    r"t\.bilibili\.com/(\d+)",
    # https://t.bilibili.com/h5/dynamic/detail/123456789012345678
    r"t\.bilibili\.com/h5/dynamic/detail/(\d+)",
    # https://www.bilibili.com/opus/123456789012345678
    r"bilibili\.com/opus/(\d+)",
]


async def handle(match) -> Illust:
    dynamic_id = match.group(1)
    db = Database().driver()
    collection = db.collection(COLLECTION)

    illust = await Bilibili().fetch(dynamic_id)
    illust.metadata["collected_at"] = time()
    await collection.insert(int(dynamic_id), illust.metadata)
    return illust
