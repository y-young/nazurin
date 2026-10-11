import re

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Pawchive
from .config import COLLECTION

patterns = [
    # https://pawchive.pw/fanbox/user/12345/post/12345
    # https://pawchive.pw/patreon/user/12345/post/12345
    # https://pawchive.pw/discord/user/12345/post/12345
    # https://pawchive.st/fanbox/user/12345/post/12345
    # https://pawchive.pw/fanbox/user/12345/post/12345/revision/12345
    r"pawchive\.(?:pw|st)/(\w+)/user/([\w-]+)/post/([\w-]+)(?:/revision/(\d+))?",
]


async def handle(match: re.Match) -> HandlerResult:
    service = match.group(1)
    user_id = match.group(2)
    post_id = match.group(3)
    revision_id = match.group(4)
    illust = await Pawchive().fetch(service, user_id, post_id, revision_id)
    document = Document(id=illust.id, collection=COLLECTION, data=illust.metadata)
    return illust, document
