import re

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Bilibili
from .config import COLLECTION

patterns = [
    # https://t.bilibili.com/123456789012345678
    r"t\.bilibili\.com/(\d+)",
    # https://t.bilibili.com/h5/dynamic/detail/123456789012345678
    r"t\.bilibili\.com/h5/dynamic/detail/(\d+)",
    # https://www.bilibili.com/opus/123456789012345678
    r"bilibili\.com/opus/(\d+)",
]


async def handle(match: re.Match) -> HandlerResult:
    dynamic_id = match.group(1)
    illust = await Bilibili().fetch(dynamic_id)
    documnet = Document(id=illust.id, collection=COLLECTION, data=illust.metadata)
    return illust, documnet
