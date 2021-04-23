from nazurin.config import env

PRIORITY = 10

COLLECTION = 'pixiv'
DOCUMENT = 'pixiv'

with env.prefixed('PIXIV_'):
    REFRESH_TOKEN = env.str('TOKEN', default=None)

    IMG_PROXY = env.str('MIRROR', default='i.pximg.net')
    TRANSLATION = env.str('TRANSLATION', default=None)

HEADERS = {'Referer': 'https://app-api.pixiv.net/'}
