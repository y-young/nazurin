import os

ENV = os.environ.get('ENV')
TOKEN = os.environ.get('TOKEN')
# Port is given by Heroku
PORT = int(os.environ.get('PORT', '8443'))

DOWNLOAD_DIR = './downloads/' # Requires a slash on the end
UPLOAD_DIR = 'pics'

ALBUM = int(os.environ.get('ALBUM'))
GALLERY = int(os.environ.get('GALLERY'))
ADMIN_ID = int(os.environ.get('ADMIN_ID'))

PIXIV_USER = os.environ.get('PIXIV_USER')
PIXIV_PASS = os.environ.get('PIXIV_PASS')

MEGA_USER = os.environ.get('MEGA_USER')
MEGA_PASS = os.environ.get('MEGA_PASS')