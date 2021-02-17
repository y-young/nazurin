from os import environ

PRIORITY = 10

REFRESH_TOKEN = environ.get('PIXIV_TOKEN', None)

COLLECTION = 'pixiv'
DOCUMENT = 'pixiv'

IMG_PROXY = environ.get('PIXIV_MIRROR', 'i.pixiv.cat')
TRANSLATION = environ.get('PIXIV_TRANSLATION', None)
