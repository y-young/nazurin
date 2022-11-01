from nazurin.config import env

PRIORITY = 9
COLLECTION = 'zerochan'

with env.prefixed('ZEROCHAN_'):
    with env.prefixed('FILE_'):
        DESTINATION: str = env.str('PATH', default='Zerochan')
