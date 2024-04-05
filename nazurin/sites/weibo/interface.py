import re

from nazurin.models import Document
from nazurin.sites import HandlerResult

from .api import Weibo
from .config import COLLECTION

patterns = [
    # https://weibo.com/1804342520/KEli42z4q
    r"weibo\.(?:com|cn)/\d+/([0-9a-zA-Z]+)",
    # https://m.weibo.cn/detail/KEli42z4q
    # https://m.weibo.cn/detail/4696149640611470
    # https://m.weibo.cn/status/4696149640611470
    r"m\.weibo\.(?:com|cn)/(?:detail|status)/([0-9a-zA-Z]+)",
    # https://weibo.cn/appurl?scheme=sinaweibo%3A%2F%2Fdetail%3Fmblogid%3D4696149640611470%26luicode%3D20000061%26lfid%3D4696149640611470&luicode=20000061&lfid=4696149640611470
    r"weibo\.cn/appurl\?[\w\%\&=]*lfid=(\d+)",
    # sinaweibo://detail?mblogid=4696149640611470&luicode=20000061&lfid=4696149640611470
    r"sinaweibo\://detail\?[\w\%\&=]*mblogid=(\d+)",
    # https://share.api.weibo.cn/share/310744244,4776731619099115.html?weibo_id=4776731619099115
    r"share\.api\.weibo\.cn/share/\d+,\d+\.html\?weibo_id=(\d+)",
]


async def handle(match: re.Match) -> HandlerResult:
    post_id = match.group(1)
    illust = await Weibo().fetch(post_id)
    document = Document(id=illust.id, collection=COLLECTION, data=illust.metadata)
    return illust, document
