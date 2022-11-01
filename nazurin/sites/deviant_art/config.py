from nazurin.config import env

PRIORITY = 10
COLLECTION = 'deviantart'

with env.prefixed('DEVIANT_ART_'):
    with env.prefixed('FILE_'):
        DESTINATION: str = env.str('PATH', default='DeviantArt')
