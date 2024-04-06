import re

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Lofter
from .config import COLLECTION

patterns = [
    # https://username.lofter.com/post/1a2b3c4d_1a2b3c4d5
    r"(\w+)\.lofter\.com/post/(\w+)",
]


async def handle(match: re.Match) -> HandlerResult:
    username = match.group(1)
    permalink = match.group(2)
    post = await Lofter().fetch(username, permalink)
    document = Document(id=post.id, collection=COLLECTION, data=post.metadata)
    return post, document
