from .api import Twitter

PRIORITY = 5
patterns = [
    # https://twitter.com/i/web/status/1234567890123456789
    # https://twitter.com/abcdefg/status/1234567890123456789
    # https://mobile.twitter.com/abcdefg/status/1234567890123456789
    r'(?:mobile\.)?twitter\.com/[^.]+/status/(\d+)'
]

def handle(match, **kwargs):
    id = match.group(1)
    imgs = Twitter().download(id)
    return imgs