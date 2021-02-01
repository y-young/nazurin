from nazurin.config import env

PRIORITY = 10

COLLECTION = 'pixiv'
DOCUMENT = 'pixiv'

with env.prefixed('PIXIV_'):
    USER = env.str('USER')
    PASSWORD = env.str('PASS')

    IMG_PROXY = env.str('MIRROR', default='i.pximg.net')
    TRANSLATION = env.str('TRANSLATION', default=None)
