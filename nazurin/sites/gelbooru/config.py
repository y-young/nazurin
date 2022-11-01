from nazurin.config import env

PRIORITY = 8
COLLECTION = 'gelbooru'

with env.prefixed('GELBOORU_'):
    with env.prefixed('FILE_'):
        DESTINATION: str = env.str('PATH', default='Gelbooru')
