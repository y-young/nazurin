from os import environ
from config import NAZURIN_DATA, STORAGE_DIR
from database import Database
from utils import logger
import requests

OD_FOLDER = STORAGE_DIR
OD_CLIENT = environ.get('OD_CLIENT')
OD_SECRET = environ.get('OD_SECRET')
OD_RD_URL = environ.get('OD_RD_URL', r'http://localhost/getAToken') # Application redirect_url
OD_RF_TOKEN = environ.get('OD_RF_TOKEN', None) # Refresh token for the first auth

OD_DOCUMENT = 'onedrive'

TOKEN_ENDPOINT = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'

class OneDrive(object):
    """Onedrive driver."""
    db = Database().driver()
    collection = db.collection(NAZURIN_DATA)
    document = collection.document(OD_DOCUMENT)
    initialize = False
    refresh_token = None

    folder_id = None

    def __init__(self):
        self.auth()
        # To find the folder and its id
        url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
        folders = dict(self._request('GET', url))
        folders = folders.get('value')
        for folder in folders:
            if folder['name'] == OD_FOLDER:
                self.folder_id = folder['id']
                break
        else:
            # create a folder
            body = {"name": OD_FOLDER, "folder": {}}
            result = self._request('POST', url, json=body)
            if result.get('id'):
                self.folder_id = result['id']

    def store(self, files):
        self.auth()
        for item in files:
            # decorate upload api url
            url = 'https://graph.microsoft.com/v1.0/me/drive/items/{parent_id}:/{filename}:/content'.format(parent_id=self.folder_id, filename=item.name)
            file = open(item.path, mode='rb')
            self._request('PUT', url, files={'file':file})
            file.close()

    def auth(self):
        # Get a refresh_token
        token_dict = self.document.get()
        if token_dict:
            refresh_token = token_dict['refresh_token']
        else:
            if OD_RF_TOKEN:
                refresh_token = OD_RF_TOKEN
            else:
                return
        # Make a request
        data = {
            'client_id': OD_CLIENT,
            'client_secret': OD_SECRET,
            'redirect_url': OD_RD_URL,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        response = requests.post(TOKEN_ENDPOINT, data=data)
        response = self._parse(response)
        # error handler place
        if response.get('access_token'):
            self.token = response['access_token']
            logger.info('OneDrive logged in')
            # Update refresh token
            refresh_token = response['refresh_token']
            if self.initialize:
                self.document.update(refresh_token)
            else:
                self.collection.insert(OD_DOCUMENT, refresh_token)
                self.initialize = True
            logger.info('OneDrive refresh token cached')

    def _request(self, method, url, headers=None, **kwargs):
        _header = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }
        if headers:
            _header.update(headers)
        if 'files' not in kwargs:
            _header['Content-Type'] = 'application/json'
        return self._parse(requests.request(method, url, headers=_header, **kwargs))

    def _parse(response):
        if 'application/json' in response.headers['Content-Type']:
            r = response.json()
        else:
            r = response.content
        return r