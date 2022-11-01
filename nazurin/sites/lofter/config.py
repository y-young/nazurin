from nazurin.config import env

PRIORITY = 8
COLLECTION = 'lofter'

with env.prefixed('LOFTER_'):
    with env.prefixed('FILE_'):
        DESTINATION: str = env.str('PATH', default='Lofter')
