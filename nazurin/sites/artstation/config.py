from nazurin.config import env

PRIORITY = 10
COLLECTION = 'artstation'

with env.prefixed('ARTSTATION_'):
    with env.prefixed('FILE_'):
        DESTINATION: str = env.str('PATH', default='Artstation')
        FILENAME: str = env.str('NAME',
                                default='{title} ({hash_id}) - {filename}')
