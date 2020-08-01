from .api import Moebooru

PRIORITY = 15
patterns = [
    # https://yande.re/post/show/123456
    r'(yande\.re)/post/show/(\d+)',

    # https://files.yande.re/image/1234567890abcdef1234567890abcdef/yande.re%20123456%20aaa-bbb%20ccc_ddd%20ddd%20eee.jpg
    r'(?:[^.]+\.)?(yande\.re)/(?:image|jpeg|sample)/[a-f0-9]{32}/yande\.re%20(\d+)',

    # https://konachan.com/post/show/123456
    r'(konachan\.com)/post/show/(\d+)',

    # https://konachan.com/image/1234567890abcdef1234567890abcdef/Konachan.com%20-%20123456%20aaa-bbb%20ccc_ddd%20ddd%20eee.jpg
    r'(?:[^.]+\.)?(konachan\.com)/(?:image|jpeg|sample)/[a-f0-9]{32}/Konachan\.com%20-%20(\d+)'
]

def handle(match, **kwargs):
    site_url = match.group(1)
    id = match.group(2)
    api = Moebooru().site(site_url)
    imgs = api.download(id)
    return imgs