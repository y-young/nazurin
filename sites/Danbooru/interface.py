from .api import Danbooru

PRIORITY = 30
patterns = [
    # https://danbooru.donmai.us/posts/123456
    r'(danbooru)\.donmai\.us/posts/(\d+)',

    # https://safebooru.donmai.us/posts/123456
    r'(safebooru)\.donmai\.us/posts/(\d+)'
]

def handle(match, **kwargs):
    site = match.group(1)
    post_id = match.group(2)
    imgs = Danbooru(site).download(post_id)
    return imgs