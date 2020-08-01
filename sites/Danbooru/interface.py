from .api import Danbooru

PRIORITY = 30
patterns = [
    # https://danbooru.donmai.us/posts/123456
    r'danbooru\.donmai\.us/posts/(\d+)'
]

def handle(match, **kwargs):
    id = match.group(1)
    imgs = Danbooru().download(id)
    return imgs