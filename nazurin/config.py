import logging
from os import path

from environs import Env

logging.basicConfig(
    format='%(asctime)s - %(name)s.%(module)s - %(levelname)s - %(message)s',
    level=logging.INFO)

env = Env()
# read config from .env file if exists
env.read_env()

ENV = env.str('ENV', default='production')
TOKEN = env.str('TOKEN')

# Webhook url, eg: https://xxx.fly.dev/, should end with '/'
WEBHOOK_URL = env.str('WEBHOOK_URL', default=None)
# Port is automatically set if on Heroku or fly.io
PORT = env.int('PORT', default=80)

STORAGE = env.list('STORAGE', subcast=str, default=['Local'])
STORAGE_DIR = env.str('STORAGE_DIR', default='Pictures')

DATABASE = env.str('DATABASE', default='Local')
# Nazurin data collection in database
NAZURIN_DATA = 'nazurin'
# Ignored items in image caption
CAPTION_IGNORE = env.list('CAPTION_IGNORE', subcast=str, default=[])

GALLERY_ID = env.int('GALLERY_ID', default=None)

ADMIN_ID = env.int('ADMIN_ID')
IS_PUBLIC = env.bool('IS_PUBLIC', default=False)
# If IS_PUBLIC is True, the following items will be ignored
ALLOW_ID = env.list('ALLOW_ID', subcast=int, default=[])
ALLOW_USERNAME = env.list('ALLOW_USERNAME', default=[])
ALLOW_GROUP = env.list('ALLOW_GROUP', subcast=int, default=[])

RETRIES = env.int('RETRIES', default=5)
TIMEOUT = env.int('TIMEOUT', default=20)
PROXY = env.str('HTTP_PROXY', default=None)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
    AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/90.0.4430.85 \
    Safari/537.36"

# Local directory to store database and temporary files
DATA_DIR = 'data'
TEMP_DIR = path.join(DATA_DIR, 'temp')
