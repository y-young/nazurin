from os import environ
from config import NAZURIN_DATA
from database import Database
from utils import logger
from microsoftgraph.client import Client
import msal

OD_FOLDER = environ.get('OD_FOLDER','Pictures')
OD_CLIENT = environ.get('OD_CLIENT')
OD_SECRET = environ.get('OD_SECRET')
OD_RD_URL = environ.get('OD_RD_URL',r'http://localhost/get_token')
OD_RF_TOKEN = environ.get('OD_RF_TOKEN',None)

OD_DOCUMENT = 'onedrive'

class OneDrive(object):
    """Onedrive driver."""
    api = Client(OD_CLIENT,OD_SECRET)
    db = Database().driver()
    collection = db.collection(NAZURIN_DATA)
    document = collection.document(OD_DOCUMENT)
    initialize = False
    refresh_token =None

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
            body = {"name": "Pictures","folder": {}}
            result = self.api._post(url,json=body)
            if result.get('id'):
                self.folder_id = result['id']

    def auth(self):
        token_dict = self.document.get()
        refresh_token = ''
        if token_dict:
            refresh_token = token_dict['refresh_token']
        else:
            if OD_RF_TOKEN:
                refresh_token = OD_RF_TOKEN
            else:
                return
        token = self.api.refresh_token(OD_RD_URL,refresh_token)
        token = self.api.set_token(token)
        logger.info('OneDrive logged in')

        # Update refresh token
        auth_api = msal.ClientApplication(OD_CLIENT,OD_SECRET)
        refresh_token = auth_api.acquire_token_by_refresh_token(refresh_token,["https://graph.microsoft.com/.default"])
        if self.initialize:
            self.document.update(refresh_token)
        else:
            self.collection.insert(OD_DOCUMENT,refresh_token)
            self.initialize = True
        logger.info('OneDrive refresh token cached')
        
    def store(self, files):
        self.auth()
        for item in files:
            # decorate upload api url
            url = 'https://graph.microsoft.com/v1.0/me/drive/items/{parent_id}:/{filename}:/content'.format(parent_id=self.folder_id,filename=item.name)
            # for _put() method create a dict
            file = dict()
            file[item.name] = open(item.path,mode='rb')
            self.api._put(url,files=file)


        

