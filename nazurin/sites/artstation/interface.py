import re

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Artstation
from .config import COLLECTION

patterns = [
    # https://www.artstation.com/artwork/2x3LaB
    # https://catzz.artstation.com/projects/A9ELeq
    r"artstation\.com/(?:artwork|projects)/([0-9a-zA-Z]+)",
]


async def handle(match: re.Match) -> HandlerResult:
    post_id = match.group(1)
    illust = await Artstation().fetch(post_id)
    document = Document(id=illust.id, collection=COLLECTION, data=illust.metadata)
    return illust, document
