from time import time

from nazurin.database import Database
from nazurin.models import Illust

from .api import Bluesky
from .config import COLLECTION

patterns = [
    # https://bsky.app/profile/shiratamacaron.bsky.social/post/3kkt7oj5rmw2j
    r"bsky\.app/profile/([\w\d\.-]+)/post/(\w+)"
]


async def handle(match) -> Illust:
    user_handle = match.group(1)
    post_rkey = match.group(2)
    db = Database().driver()
    collection = db.collection(COLLECTION)

    illust = await Bluesky().fetch(user_handle, post_rkey)
    illust.metadata["collected_at"] = time()
    await collection.insert("_".join([user_handle, post_rkey]), illust.metadata)
    return illust
