from nazurin.config import env

PRIORITY = 4
COLLECTION = 'bilibili'

with env.prefixed('BILIBILI_'):
    with env.prefixed('FILE_'):
        DESTINATION: str = env.str('PATH', default='Bilibili')
