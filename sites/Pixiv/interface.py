from .api import Pixiv

PRIORITY = 10
patterns = [
    # https://pixiv.net/i/123456
    # https://pixiv.net/artworks/123456
    # https://www.pixiv.net/member_illust.php?mode=medium&illust_id=123456
    r'(?:www\.)?pixiv\.net/(?:(?:i|artworks)/|member_illust\.php\?(?:mode=[a-z_]*&)?illust_id=)(\d+)',

    # https://i.pximg.net/img-original/img/2020/02/02/20/00/02/123456_p0.png
    # https://i-f.pximg.net/img-original/img/2020/02/02/20/00/02/123456_p0.png
    # https://i.pximg.net/img-master/img/2020/02/02/20/00/02/123456_p0_master1200.jpg
    # https://i.pximg.net/c/540x540_10_webp/img-master/img/2020/02/02/20/00/02/123456_p0_square1200.jpg
    r'[^./]+\.(?:pximg|pixiv)\.net/(?:\w+/)*img-[a-z-]+/img/\d{4}/\d{2}/\d{2}/\d{2}/\d{2}/\d{2}/(\d+)'
]

def handle(match, **kwargs):
    artwork_id = match.group(1)
    api = Pixiv()
    if kwargs['is_admin']:
        api.bookmark(artwork_id)
    imgs = api.download(artwork_id)
    return imgs