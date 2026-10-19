import re

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Kemono
from .config import COLLECTIONS, Site

patterns = [
    # https://kemono.party/fanbox/user/12345/post/12345
    # https://kemono.party/patreon/user/12345/post/12345
    # https://kemono.party/fantia/user/12345/post/12345
    # https://kemono.party/boosty/user/abcdef/post/a1b2c3-d4e5f6-7890
    # https://kemono.party/dlsite/user/RG12345/post/RE12345
    # https://kemono.party/gumroad/user/12345/post/aBc1d2
    # https://kemono.cr/subscribestar/user/abcdef/post/12345
    # https://kemono.cr/fanbox/user/12345/post/12345/revision/12345
    r"(kemono)\.(?:party|su|cr)/(\w+)/user/([\w-]+)/post/([\w-]+)(?:/revision/(\d+))?",
    # https://pawchive.pw/fanbox/user/12345/post/12345
    # https://pawchive.st/fanbox/user/12345/post/12345
    r"(pawchive)\.(?:pw|st)/(\w+)/user/([\w-]+)/post/([\w-]+)(?:/revision/(\d+))?",
]


async def handle(match: re.Match) -> HandlerResult:
    site = Site(match.group(1))
    service = match.group(2)
    user_id = match.group(3)
    post_id = match.group(4)
    revision_id = match.group(5)
    illust = await Kemono(site).fetch(service, user_id, post_id, revision_id)
    document = Document(
        id=illust.id,
        collection=COLLECTIONS[site],
        data=illust.metadata,
    )
    return illust, document
