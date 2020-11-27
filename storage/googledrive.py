import json
from os import environ
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive as GDrive
from oauth2client.service_account import ServiceAccountCredentials
from config import DOWNLOAD_DIR
from utils import NazurinError

GD_FOLDER = environ.get('GD_FOLDER')
GD_CREDENTIALS = environ.get('GD_CREDENTIALS', environ.get('GOOGLE_APPLICATION_CREDENTIALS'))

class GoogleDrive(object):
    """Google Drive driver."""
    drive = None

    def __init__(self):
        """Initialize and log in."""
        self.auth()

    def auth(self):
        if GoogleDrive.drive:
            return
        gauth = GoogleAuth()
        scope = ['https://www.googleapis.com/auth/drive']
        gauth.auth_method = 'service'
        if GD_CREDENTIALS:
            if GD_CREDENTIALS.startswith('{'):
                credentials = json.loads(GD_CREDENTIALS)
                gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
            else:
                gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(GD_CREDENTIALS, scope)
        else:
            raise NazurinError('Credentials not found for Google Drive storage.')
        GoogleDrive.drive = GDrive(gauth)

    def store(self, files):
        for item in files:
            metadata = {
                'title': item.name,
                'parents': [{'id': GD_FOLDER}]
            }
            f = GoogleDrive.drive.CreateFile(metadata)
            f.SetContentFile(item.path)
            f.Upload()

    def findFolder(self, name):
        query = {
            'q': "mimeType='application/vnd.google-apps.folder' and title='" + name + "'",
            'spaces': 'drive'
        }
        result = GoogleDrive.drive.ListFile(query).GetList()
        return result[0].get('id')

    def createFolder(self, name):
        metadata = {
            'title': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [{'id': GD_FOLDER}]
        }
        folder = GoogleDrive.drive.CreateFile(metadata)
        folder.Upload()
        return folder.get('id')