from os import environ
from microsoftgraph.client import Client

OD_FOLDER = environ.get('OD_FOLDER','Pictures')
OD_CLIENT = environ.get('OD_CLIENT')
OD_SECRET = environ.get('OD_SECRET')
OD_RD_URL = environ.get('OD_RD_URL',r'http://localhost')
OD_RF_TOKEN = environ.get('OD_RF_TOKEN')

class OneDrive(object):
    """Onedrive driver."""
    folder_id = None

    def __init__(self): # To find the folder and its id
        if not self.folder_id:
            od = self.auth()
            # seek
            folders = dict(od.drive_root_children_items())
            folders = folders.get('value')
            for folder in folders:
                if folder['name'] == OD_FOLDER:
                    self.folder_id = folder['id']
                    break
            else:
                # create a folder
                url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
                body = {"name": "Pictures","folder": {}}
                result = od._post(url,json=body)
                if result.get('id'):
                    self.folder_id = result['id']

    def auth(self):
        try:
            od = Client(OD_CLIENT,OD_SECRET)
            token = od.refresh_token(OD_RD_URL,OD_RF_TOKEN)
            token = od.set_token(token)
        except:
            od = None
        return od
        
    def update_token(self):
        pass
    def store(self, files):
        od = self.auth()
        for item in files:
            # decorate upload api url
            url = 'https://graph.microsoft.com/v1.0/me/drive/items/{parent_id}:/{filename}:/content'.format(parent_id=self.folder_id,filename=item.name)
            # for _put() method create a dict
            file = dict()
            file[item.name] = open(item.path)
            od._put(url,files=file)


        

