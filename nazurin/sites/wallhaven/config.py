from nazurin.config import env

PRIORITY = 9
COLLECTION = 'wallhaven'

with env.prefixed('WALLHAVEN_'):
    API_KEY = env.str('API_KEY', default=None)
