from time import time

from nazurin.database import Database
from nazurin.models import Illust

from .api import Artstation
from .config import COLLECTION

patterns = [
    # https://www.artstation.com/artwork/2x3LaB
    r'artstation\.com/artwork/([0-9a-zA-Z]+)'
]

async def handle(match, **kwargs) -> Illust:
    post_id = match.group(1)
    db = Database().driver()
    collection = db.collection(COLLECTION)

    illust = await Artstation().fetch(post_id)
    illust.metadata['collected_at'] = time()
    await collection.insert(post_id, illust.metadata)
    return illust
