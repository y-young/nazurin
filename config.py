import os
import logging

ENV = os.environ.get('ENV', 'production')
TOKEN = os.environ.get('TOKEN')
# Webhook url, eg: https://xxx.herokuapp.com/, should end with '/'
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
# Port is given by Heroku
PORT = int(os.environ.get('PORT', '8443'))

STORAGE = eval(os.environ.get('STORAGE', '[]'))
DOWNLOAD_DIR = './downloads/' # Requires a slash on the end
UPLOAD_DIR = 'Pictures'

DATABASE = os.environ.get('DATABASE', 'Local')
# nazurin data collection in database
NAZURIN_DATA = 'nazurin'

ALBUM_ID = int(os.environ.get('ALBUM_ID'))
GALLERY_ID = int(os.environ.get('GALLERY_ID'))
ADMIN_ID = int(os.environ.get('ADMIN_ID'))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('bot')