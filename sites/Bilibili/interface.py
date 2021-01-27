from time import time

from database import Database

from .api import Bilibili
from .config import COLLECTION

patterns = [
    # https://t.bilibili.com/123456789012345678
    r't\.bilibili\.com/(\d+)',

    # https://t.bilibili.com/h5/dynamic/detail/123456789012345678
    r't\.bilibili\.com/h5/dynamic/detail/(\d+)'
]

def handle(match, **kwargs):
    dynamic_id = match.group(1)
    db = Database().driver()
    collection = db.collection(COLLECTION)

    imgs, data = Bilibili().fetch(dynamic_id)
    data['collected_at'] = time()
    collection.insert(int(dynamic_id), data)
    return imgs
