import re

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Bluesky
from .config import COLLECTION

patterns = [
    # https://atproto.com/specs/record-key#record-key-syntax
    # https://bsky.app/profile/shiratamacaron.bsky.social/post/3kkt7oj5rmw2j
    r"bsky\.app/profile/([\w\.\-]+)/post/([\w\.\-~]+)",
]


async def handle(match: re.Match) -> HandlerResult:
    user_handle = match.group(1)
    post_rkey = match.group(2)
    illust = await Bluesky().fetch(user_handle, post_rkey)
    document = Document(
        id=illust.id,
        collection=COLLECTION,
        data=illust.metadata,
    )
    return illust, document
