import re

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Zerochan
from .config import COLLECTION

patterns = [
    # https://www.zerochan.net/123456
    r"zerochan\.net/(\d+)",
    # https://s1.zerochan.net/Abcdef.600.123456.jpg
    # https://static.zerochan.net/Abcdef.full.123456.jpg
    r"zerochan\.net/\S+\.(\d+)\.\w+$",
]


async def handle(match: re.Match) -> HandlerResult:
    post_id = match.group(1)
    api = Zerochan()
    illust = await api.view(int(post_id))
    document = Document(id=illust.id, collection=COLLECTION, data=illust.metadata)
    return illust, document
