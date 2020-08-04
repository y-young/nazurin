from .api import Bilibili
PRIORITY = 4

patterns = [
    # https://t.bilibili.com/123456789012345678
    r't\.bilibili\.com/(\d+)',

    # https://t.bilibili.com/h5/dynamic/detail/123456789012345678
    r't\.bilibili\.com/h5/dynamic/detail/(\d+)'
]

def handle(match, **kwargs):
    id = match.group(1)
    imgs = Bilibili().download(id)
    return imgs