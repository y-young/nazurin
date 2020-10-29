from os import environ

PRIORITY = 10

USER = environ.get('PIXIV_USER')
PASSWORD = environ.get('PIXIV_PASS')

COLLECTION = 'pixiv'
DOCUMENT = 'pixiv'

IMG_PROXY = environ.get('PIXIV_MIRROR', 'i.pixiv.cat')