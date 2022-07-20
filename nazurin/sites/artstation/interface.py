from time import time

from nazurin.database import Database
from nazurin.models import Illust

from .api import Artstation
from .config import COLLECTION

patterns = [
    # https://www.artstation.com/artwork/2x3LaB
    # https://catzz.artstation.com/projects/A9ELeq
    r'artstation\.com/(?:artwork|projects)/([0-9a-zA-Z]+)'
]

async def handle(match) -> Illust:
    post_id = match.group(1)
    db = Database().driver()
    collection = db.collection(COLLECTION)

    illust = await Artstation().fetch(post_id)
    illust.metadata['collected_at'] = time()
    await collection.insert(post_id, illust.metadata)
    return illust
