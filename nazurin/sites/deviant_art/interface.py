import re

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import DeviantArt
from .config import COLLECTION

patterns = [
    # https://www.deviantart.com/username/art/Title-of-Deviation-123456789
    r"(?:www\.)?deviantart\.com/[\w-]+/art/[\w-]+-(\d+)",
    # https://username.deviantart.com/art/Title-of-Deviation-123456789
    r"[\w-]+\.deviantart\.com/art/[\w-]+-(\d+)",
]


async def handle(match: re.Match) -> HandlerResult:
    post_id = match.group(1)
    illust = await DeviantArt().fetch(post_id)
    document = Document(id=illust.id, collection=COLLECTION, data=illust.metadata)
    return illust, document
