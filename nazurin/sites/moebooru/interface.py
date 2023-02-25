from time import time

from nazurin.database import Database
from nazurin.models import Illust

from .api import Moebooru
from .config import COLLECTIONS

patterns = [
    # https://yande.re/post/show/123456
    r"(yande\.re)/post/show/(\d+)",
    # https://files.yande.re/image/1234567890abcdef1234567890abcdef/yande.re%20123456%20aaa-bbb%20ccc_ddd%20ddd%20eee.jpg
    r"(?:[^.]+\.)?(yande\.re)/(?:image|jpeg|sample)/[a-f0-9]{32}/yande\.re%20(\d+)",
    # https://konachan.com/post/show/123456
    r"(konachan\.com)/post/show/(\d+)",
    # https://konachan.com/image/1234567890abcdef1234567890abcdef/Konachan.com%20-%20123456%20aaa-bbb%20ccc_ddd%20ddd%20eee.jpg
    r"(?:[^.]+\.)?(konachan\.com)/(?:image|jpeg|sample)"
    r"/[a-f0-9]{32}/Konachan\.com%20-%20(\d+)",
    # https://lolibooru.moe/post/show/123456
    r"(lolibooru\.moe)/post/show/(\d+)",
    # https://lolibooru.moe/image/1234567890abcdef1234567890abcdef/lolibooru%20123456%20aaa-bbb%20ccc_ddd%20ddd%20eee.jpg
    r"(lolibooru\.moe)/(?:image|jpeg|sample)/[a-f0-9]{32}/lolibooru%20(\d+)",
]


async def handle(match) -> Illust:
    site_url = match.group(1)
    post_id = match.group(2)
    db = Database().driver()
    collection = db.collection(COLLECTIONS[site_url])
    api = Moebooru().site(site_url)

    illust = await api.view(post_id)
    illust.metadata["collected_at"] = time()
    await collection.insert(int(post_id), illust.metadata)
    return illust
