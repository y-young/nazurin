import re

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Twitter
from .config import COLLECTION

patterns = [
    # https://twitter.com/i/web/status/1234567890123456789
    # https://twitter.com/abcdefg/status/1234567890123456789
    # https://www.twitter.com/abcdefg/status/1234567890123456789
    # https://mobile.twitter.com/abcdefg/status/1234567890123456789
    r"(?:mobile\.|www\.)?(?:twitter|x)\.com/[^.]+/status/(\d+)",
]


async def handle(match: re.Match) -> HandlerResult:
    status_id = match.group(1)
    illust = await Twitter().fetch(int(status_id))
    document = Document(id=illust.id, collection=COLLECTION, data=illust.metadata)
    return illust, document
