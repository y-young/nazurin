from enum import Enum

from nazurin.config import env

class PixivPrivacy(Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'

PRIORITY = 10

COLLECTION = 'pixiv'
DOCUMENT = 'pixiv'

with env.prefixed('PIXIV_'):
    REFRESH_TOKEN = env.str('TOKEN', default=None)

    IMG_PROXY = env.str('MIRROR', default='i.pximg.net')
    TRANSLATION = env.str('TRANSLATION', default=None)
    BOOKMARK_PRIVACY = env.enum('BOOKMARK_PRIVACY',
                                type=PixivPrivacy,
                                default=PixivPrivacy.PUBLIC.value,
                                ignore_case=True)

HEADERS = {'Referer': 'https://app-api.pixiv.net/'}
