from ast import literal_eval
from os import environ

ENV = environ.get('ENV', 'production')
TOKEN = environ.get('TOKEN')
# Webhook url, eg: https://xxx.herokuapp.com/, should end with '/'
WEBHOOK_URL = environ.get('WEBHOOK_URL')
# Port is given by Heroku
PORT = int(environ.get('PORT', '8443'))

STORAGE = literal_eval(environ.get('STORAGE', '[]'))
DOWNLOAD_DIR = './downloads/' # Requires a slash on the end
STORAGE_DIR = environ.get('STORAGE_DIR', 'Pictures')

DATABASE = environ.get('DATABASE', 'Local')
# nazurin data collection in database
NAZURIN_DATA = 'nazurin'

ALBUM_ID = int(environ.get('ALBUM_ID'))
GALLERY_ID = int(environ.get('GALLERY_ID'))
ADMIN_ID = int(environ.get('ADMIN_ID'))

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
RETRIES = 5