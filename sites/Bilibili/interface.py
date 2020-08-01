from .api import Bilibili
PRIORITY = 4

patterns = [
    # https://t.bilibili.com/123456789012345678
    r't\.bilibili\.com/(\d+)'
]

def handle(match, **kwargs):
    id = match.group(1)
    imgs = Bilibili().download(id)
    return imgs