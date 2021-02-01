import logging

from environs import Env

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

env = Env()
# read config from .env file if exists
env.read_env()

ENV = env.str('ENV', default='production')
TOKEN = env.str('TOKEN')

# Webhook url, eg: https://xxx.herokuapp.com/, should end with '/'
WEBHOOK_URL = env.str('WEBHOOK_URL', default=None)
# Port is given by Heroku
PORT = env.int('PORT', default=8443)

TEMP_DIR = './temp/'
STORAGE = env.list('STORAGE', subcast=str, default=['Local'])
STORAGE_DIR = env.str('STORAGE_DIR', default='Pictures')

DATABASE = env.str('DATABASE', default='Local')
# Nazurin data collection in database
NAZURIN_DATA = 'nazurin'
# Ignored items in image caption
CAPTION_IGNORE = env.list('CAPTION_IGNORE', subcast=str, default=[])

ALBUM_ID = env.int('ALBUM_ID')
GALLERY_ID = env.int('GALLERY_ID')

IS_PUBLIC = env.bool('IS_PUBLIC', default=False)
# If IS_PUBLIC is True, the following items will be ignored
ALLOW_ID = env.list('ALLOW_ID', subcast=int, default=[])
ALLOW_USERNAME = env.list('ALLOW_USERNAME', default=[])
ALLOW_GROUP = env.list('ALLOW_GROUP', subcast=int, default=[])

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
RETRIES = 5
