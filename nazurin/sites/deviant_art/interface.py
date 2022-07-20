from time import time

from nazurin.database import Database
from nazurin.models import Illust

from .api import DeviantArt
from .config import COLLECTION

patterns = [
    # https://www.deviantart.com/username/art/Title-of-Deviation-123456789
    r'(?:www\.)?deviantart\.com/[\w-]+/art/[\w-]+-(\d+)',

    # https://username.deviantart.com/art/Title-of-Deviation-123456789
    r'[\w-]+\.deviantart\.com/art/[\w-]+-(\d+)'
]

async def handle(match) -> Illust:
    post_id = match.group(1)
    db = Database().driver()
    collection = db.collection(COLLECTION)

    illust = await DeviantArt().fetch(post_id)
    illust.metadata['collected_at'] = time()
    await collection.insert(post_id, illust.metadata)
    return illust
