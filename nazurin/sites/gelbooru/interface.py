import re

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Gelbooru
from .config import COLLECTION

patterns = [
    # https://gelbooru.com/index.php?page=post&s=view&id=123456
    r"gelbooru\.com/index\.php\?page=post&s=view&id=(\d+)",
]


async def handle(match: re.Match) -> HandlerResult:
    post_id = match.group(1)
    illust = await Gelbooru().fetch(post_id)
    document = Document(id=illust.id, collection=COLLECTION, data=illust.metadata)
    return illust, document
