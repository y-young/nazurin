from time import time

from nazurin.database import Database
from nazurin.models import Illust

from .api import Twitter
from .config import COLLECTION

patterns = [
    # https://twitter.com/i/web/status/1234567890123456789
    # https://twitter.com/abcdefg/status/1234567890123456789
    # https://www.twitter.com/abcdefg/status/1234567890123456789
    # https://mobile.twitter.com/abcdefg/status/1234567890123456789
    r'(?:mobile\.|www\.)?twitter\.com/[^.]+/status/(\d+)'
]

async def handle(match, **kwargs) -> Illust:
    status_id = match.group(1)
    db = Database().driver()
    collection = db.collection(COLLECTION)
    illust = await Twitter().fetch(status_id)
    illust.metadata['collected_at'] = time()
    await collection.insert(int(status_id), illust.metadata)
    return illust
