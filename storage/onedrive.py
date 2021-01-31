from os import environ
from config import NAZURIN_DATA, STORAGE_DIR
from database import Database
from utils import logger
from microsoftgraph.client import Client
import msal
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
    api = Client(OD_CLIENT, OD_SECRET)
    db = Database().driver()
    collection = db.collection(NAZURIN_DATA)
    document = collection.document(OD_DOCUMENT)
    initialize = False
    refresh_token = None

    folder_id = None

    def __init__(self):
        self.auth()
        # To find the folder and its id
        folders = dict(self.api.drive_root_children_items())
        folders = folders.get('value')
        for folder in folders:
            if folder['name'] == OD_FOLDER:
                self.folder_id = folder['id']
                break
        else:
            # create a folder
            url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
            body = {"name": OD_FOLDER, "folder": {}}
            result = self.api._post(url, json=body)
            if result.get('id'):
                self.folder_id = result['id']

    def auth(self):
        token_dict = self.document.get()
        if token_dict:
            refresh_token = token_dict['refresh_token']
        else:
            if OD_RF_TOKEN:
                refresh_token = OD_RF_TOKEN
            else:
                return
        token = self.api.refresh_token(OD_RD_URL, refresh_token)
        token = self.api.set_token(token)
        logger.info('OneDrive logged in')

        # Update refresh token
        auth_api = msal.ClientApplication(OD_CLIENT, OD_SECRET)
        refresh_token = auth_api.acquire_token_by_refresh_token(refresh_token, ["https://graph.microsoft.com/.default"])
        if self.initialize:
            self.document.update(refresh_token)
        else:
            self.collection.insert(OD_DOCUMENT, refresh_token)
            self.initialize = True
        logger.info('OneDrive refresh token cached')

    def store(self, files):
        self.auth()
        for item in files:
            # decorate upload api url
            url = 'https://graph.microsoft.com/v1.0/me/drive/items/{parent_id}:/{filename}:/content'.format(parent_id=self.folder_id, filename=item.name)
            file = open(item.path, mode='rb')
            self.api._put(url, files={'file':file})
            file.close()

    def get_token(self, redirect_url, refresh_token):
        data = {
            'client_id': OD_CLIENT,
            'client_secret': OD_SECRET,
            'redirect_url': OD_RD_URL,
            'refresh_token': OD_RF_TOKEN,
            'grant_type': 'refresh_token'
        }
        response = requests.post(TOKEN_ENDPOINT, data=data)
        if 'application/json' in response.headers['Content-Type']:
            r = response.json()
        else:
            r = response.content
        # error handler place
        return r