import re
from urllib.parse import quote, unquote, urlsplit

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Telegraph
from .config import COLLECTION

patterns = [
    r"(?:^|,)(?P<url>(?i:https?://(?:telegra\.ph|graph\.org)/[\w%-]+))"
    r"(?=,|$)",
]


def normalize_page_url(url: str) -> tuple[str, str]:
    """Return a canonical page path and source URL."""
    parsed = urlsplit(url)
    host = parsed.hostname
    assert host is not None
    page_path = unquote(parsed.path).strip("/")
    source_url = f"https://{host}/{quote(page_path, safe='')}"
    return page_path, source_url


async def handle(match: re.Match) -> HandlerResult:
    page_path, source_url = normalize_page_url(match.group("url"))
    illust = await Telegraph().fetch(page_path, source_url)
    document = Document(id=illust.id, collection=COLLECTION, data=illust.metadata)
    return illust, document
