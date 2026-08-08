import re
from urllib.parse import unquote, urlsplit

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Telegraph
from .config import COLLECTION

patterns = [
    r"(?P<url>(?i:https?://(?:telegra\.ph|graph\.org)/[\w%-]+))",
]


def normalize_page_url(url: str) -> tuple[str, str]:
    """Return the decoded page path and original source URL."""
    parsed = urlsplit(url)
    page_path = unquote(parsed.path).strip("/")
    return page_path, url


async def handle(match: re.Match) -> HandlerResult:
    page_path, source_url = normalize_page_url(match.group("url"))
    illust = await Telegraph().fetch(page_path, source_url)
    document = Document(id=illust.id, collection=COLLECTION, data=illust.metadata)
    return illust, document
