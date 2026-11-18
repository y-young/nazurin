import re

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Xfolio
from .config import COLLECTION

patterns = [
    # https://xfolio.jp/portfolio/mucha/works/7467
    # https://xfolio.jp/zh-CHS/portfolio/mucha/works/7467
    r"xfolio\.jp/(?:[a-z]{2}(?:-[A-Za-z]+)?/)?portfolio/([^/?#]+)/works/(\d+)",
]


async def handle(match: re.Match) -> HandlerResult:
    creator = match.group(1)
    work_id = match.group(2)
    illust = await Xfolio().fetch(creator, work_id)
    document = Document(id=illust.id, collection=COLLECTION, data=illust.metadata)
    return illust, document
