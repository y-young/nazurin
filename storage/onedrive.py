from os import environ
from config import NAZURIN_DATA
from database import Database
from microsoftgraph.client import Client
import msal

OD_FOLDER = environ.get('OD_FOLDER','Pictures')
OD_CLIENT = environ.get('OD_CLIENT')
OD_SECRET = environ.get('OD_SECRET')
OD_RD_URL = environ.get('OD_RD_URL',r'http://localhost')
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
        if not self.folder_id:
            # seek
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
        refresh_token = self.document.get()
        if not refresh_token:
            if OD_RF_TOKEN:
                refresh_token=OD_RF_TOKEN
            else:
                return
        token = self.api.refresh_token(OD_RD_URL,refresh_token)
        token = self.api.set_token(token)

        # Update refresh token
        auth_api = msal.ClientApplication(OD_CLIENT,OD_SECRET)
        refresh_token = auth_api.acquire_token_by_refresh_token(refresh_token,["https://graph.microsoft.com/.default"])
        self.document.update(refresh_token)

        
    def store(self, files):
        self.auth()
        for item in files:
            # decorate upload api url
            url = 'https://graph.microsoft.com/v1.0/me/drive/items/{parent_id}:/{filename}:/content'.format(parent_id=self.folder_id,filename=item.name)
            # for _put() method create a dict
            file = dict()
            file[item.name] = open(item.path)
            self.api._put(url,files=file)


        

