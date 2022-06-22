from time import time

from nazurin.database import Database
from nazurin.models import Illust

from .api import Wallhaven
from .config import COLLECTION

patterns = [
    # http://whvn.cc/94x38z
    # https://wallhaven.cc/w/94x38z
    r'(?:wallhaven|whvn)\.cc\/(?:w\/)?([\w]+)'
]

async def handle(match, **kwargs) -> Illust:
    wallpaper_id = match.group(1)
    db = Database().driver()
    collection = db.collection(COLLECTION)
    illust = await Wallhaven().fetch(wallpaper_id)
    illust.metadata['collected_at'] = time()
    await collection.insert(wallpaper_id, illust.metadata)
    return illust
