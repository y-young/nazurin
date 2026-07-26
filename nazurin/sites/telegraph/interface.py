import re
from urllib.parse import quote, urlsplit

from nazurin.models import Document
from nazurin.sites import HandlerResult
from nazurin.utils.exceptions import NazurinError

from .api import Telegraph, validate_page_path
from .config import COLLECTION

SUPPORTED_HOSTS = {"graph.org", "telegra.ph"}

patterns = [
    r"(?P<url>(?i:https?://(?:telegra\.ph|graph\.org)/[^\s,]+))",
]


def normalize_page_url(url: str) -> tuple[str, str]:
    """Return a canonical page path and source URL."""
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as error:
        raise NazurinError("Invalid Telegraph URL") from error

    host = (parsed.hostname or "").lower()
    if (
        parsed.scheme.lower() not in {"http", "https"}
        or host not in SUPPORTED_HOSTS
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
    ):
        raise NazurinError("Invalid Telegraph URL")

    page_path = validate_page_path(parsed.path)
    source_url = f"https://{host}/{quote(page_path, safe='')}"
    return page_path, source_url


async def handle(match: re.Match) -> HandlerResult:
    page_path, source_url = normalize_page_url(match.group("url"))
    illust = await Telegraph().fetch(page_path, source_url)
    document = Document(id=illust.id, collection=COLLECTION, data=illust.metadata)
    return illust, document
