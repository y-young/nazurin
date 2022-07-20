from time import time

from nazurin.database import Database
from nazurin.models import Illust

from .api import Zerochan
from .config import COLLECTION

patterns = [
    # https://www.zerochan.net/123456
    r'zerochan\.net/(\d+)',

    # https://s1.zerochan.net/Abcdef.600.123456.jpg
    # https://static.zerochan.net/Abcdef.full.123456.jpg
    r'zerochan\.net/\S+\.(\d+)\.\w+$'
]

async def handle(match) -> Illust:
    post_id = match.group(1)
    api = Zerochan()
    db = Database().driver()
    collection = db.collection(COLLECTION)

    illust = await api.view(post_id)
    illust.metadata['collected_at'] = time()
    await collection.insert(int(post_id), illust.metadata)
    return illust
