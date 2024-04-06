import re

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Wallhaven
from .config import COLLECTION

patterns = [
    # http://whvn.cc/94x38z
    # https://wallhaven.cc/w/94x38z
    r"(?:wallhaven|whvn)\.cc\/(?:w\/)?([\w]+)",
]


async def handle(match: re.Match) -> HandlerResult:
    wallpaper_id = match.group(1)
    illust = await Wallhaven().fetch(wallpaper_id)
    document = Document(id=illust.id, collection=COLLECTION, data=illust.metadata)
    return illust, document
