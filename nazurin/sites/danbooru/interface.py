import re

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Danbooru
from .config import COLLECTION

patterns = [
    # https://danbooru.donmai.us/posts/123456
    # https://safebooru.donmai.us/posts/123456
    r"(?:danbooru|safebooru)\.donmai\.us/posts/(?P<id>\d+)",
    # https://cdn.donmai.us/original/12/ab/12ab34cd56ef7890ab12cd34ef567890.png
    r"cdn\.donmai\.us/\w+/(?:[a-f0-9]{2}/){2}(?P<md5>[a-f0-9]{32})\.",
    # https://danbooru.donmai.us/data/sample/sample-12ab34cd56ef7890ab12cd34ef567890.jpg
    # https://safebooru.donmai.us/data/___original__drawn_by__12ab34cd56ef7890ab12cd34ef567890.png
    r"(?:danbooru|safebooru)\.donmai\.us/data/(?:sample/)?(?:\S+)?"
    r"(?P<md5>[a-f0-9]{32})\.",
]


async def handle(match: re.Match) -> HandlerResult:
    api = Danbooru()
    if match.lastgroup == "id":
        post_id = match.group(1)
        illust = await api.view(post_id)
    else:
        md5 = match.group(1)
        illust = await api.view(md5=md5)

    document = Document(id=illust.id, collection=COLLECTION, data=illust.metadata)
    return illust, document
