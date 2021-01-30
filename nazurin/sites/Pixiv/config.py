from nazurin.config import env

PRIORITY = 10

USER = env.str('PIXIV_USER')
PASSWORD = env.str('PIXIV_PASS')

COLLECTION = 'pixiv'
DOCUMENT = 'pixiv'

IMG_PROXY = env.str('PIXIV_MIRROR', default='i.pximg.net')
TRANSLATION = env.str('PIXIV_TRANSLATION', default=None)
