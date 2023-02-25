from time import time

from nazurin.database import Database
from nazurin.models import Illust

from .api import Gelbooru
from .config import COLLECTION

patterns = [
    # https://gelbooru.com/index.php?page=post&s=view&id=123456
    r"gelbooru\.com/index\.php\?page=post&s=view&id=(\d+)"
]


async def handle(match) -> Illust:
    post_id = match.group(1)
    db = Database().driver()
    collection = db.collection(COLLECTION)

    illust = await Gelbooru().fetch(post_id)
    illust.metadata["collected_at"] = time()
    await collection.insert(int(post_id), illust.metadata)
    return illust
