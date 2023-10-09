from time import time

from nazurin.database import Database
from nazurin.models import Illust

from .api import Misskey
from .config import COLLECTION

patterns = [
    # https://site.example/notes/9khcu788zb
    r"://(.*?)/notes/(.*)",
]

async def handle(match) -> Illust:
    site_url = match.group(1)
    post_id = match.group(2)
    db = Database().driver()
    collection = db.collection(COLLECTION)
    
    illust = await Misskey().fetch(site_url, post_id)
    illust.metadata["collected_at"] = time()
    await collection.insert(int(post_id), illust.metadata)
    return illust
