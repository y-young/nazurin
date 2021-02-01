import time
from os import environ, path

import requests

from config import NAZURIN_DATA, STORAGE_DIR
from database import Database
from utils import logger

OD_FOLDER = STORAGE_DIR
OD_CLIENT = environ.get('OD_CLIENT')
OD_SECRET = environ.get('OD_SECRET')
OD_RF_TOKEN = environ.get('OD_RF_TOKEN',
                          None)  # Refresh token for first-time auth
OD_DOCUMENT = 'onedrive'

class OneDrive(object):
    """Onedrive driver."""
    db = Database().driver()
    collection = db.collection(NAZURIN_DATA)
    document = collection.document(OD_DOCUMENT)

    access_token = None
    refresh_token = None
    expires_at = 0
    folder_id = None

    def upload(self, file):
        # https://docs.microsoft.com/zh-cn/graph/api/driveitem-createuploadsession?view=graph-rest-1.0
        file.size = path.getsize(file.path)
        # create drive item
        create_file_url = 'https://graph.microsoft.com/v1.0/me/drive/items/{parent_id}/children'.format(
            parent_id=self.folder_id)
        body = {
            "name": file.name,
            "size": file.size,
            "file": {},
            "@microsoft.graph.conflictBehavior": "replace"
        }
        response = self._request('POST', create_file_url, json=body)
        # create upload session
        create_session_url = 'https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/createUploadSession'.format(
            item_id=response['id'])
        response = self._request('POST', create_session_url)
        # upload
        header = {
            'Content-Range':
            'bytes 0-{end}/{size}'.format(end=file.size - 1, size=file.size)
        }
        with open(file.path, mode='rb') as data:
            self._request('PUT',
                          response['uploadUrl'],
                          headers=header,
                          data=data)

    def store(self, files):
        self.requireAuth()
        if not self.folder_id:
            self.getDestination()

        for item in files:
            self.upload(item)

    def findFolder(self, name):
        self.requireAuth()
        # https://docs.microsoft.com/zh-cn/graph/api/driveitem-list-children?view=graph-rest-1.0&tabs=http
        url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
        folders = dict(self._request('GET', url))
        folders = folders.get('value')
        for folder in folders:
            if folder['name'] == name:
                return folder['id']
        return None

    def createFolder(self, name):
        self.requireAuth()
        # https://docs.microsoft.com/zh-cn/graph/api/driveitem-post-children?view=graph-rest-1.0&tabs=http
        url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
        body = {"name": name, "folder": {}}
        result = self._request('POST', url, json=body)
        return result['id']

    def requireAuth(self):
        # https://docs.microsoft.com/zh-cn/azure/active-directory/develop/v2-oauth2-auth-code-flow
        if self.access_token and self.expires_at > time.time():
            # Logged in, access_token not expired
            return

        credentials = self.document.get()
        if credentials:
            self.refresh_token = credentials['refresh_token']
            if 'folder_id' in credentials.keys():
                self.folder_id = credentials['folder_id']
            if credentials['expires_at'] > time.time():
                self.access_token = credentials['access_token']
                self.expires_at = credentials['expires_at']
                logger.info('OneDrive logged in through cached tokens')
                return
            else:
                self.auth()  # Refresh access_token
        else:
            # Database should be initialized
            self.refresh_token = OD_RF_TOKEN
            self.auth(initialize=True)

    def auth(self, initialize=False):
        # https://docs.microsoft.com/zh-cn/azure/active-directory/develop/v2-oauth2-auth-code-flow
        url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        data = {
            'client_id': OD_CLIENT,
            'client_secret': OD_SECRET,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        response = requests.post(url, data=data)
        response = self._parse(response)
        self.access_token = response['access_token']
        self.refresh_token = response['refresh_token']
        self.expires_at = time.time() + response['expires_in']
        credentials = {
            'access_token': response['access_token'],
            'refresh_token': response['refresh_token'],
            'expires_at': self.expires_at
        }
        if initialize:
            self.collection.insert(OD_DOCUMENT, credentials)
            logger.info('OneDrive logged in')
        else:
            self.document.update(credentials)
            logger.info('OneDrive access token updated')

    def getDestination(self):
        # Try to find the folder and its id
        self.folder_id = self.findFolder(OD_FOLDER)
        # Not found, create a new folder
        if not self.folder_id:
            self.folder_id = self.createFolder(OD_FOLDER)
        self.document.update({'folder_id': self.folder_id})
        logger.info('OneDrive folder ID cached')

    def _request(self, method, url, headers=None, **kwargs):
        # make a request with access token
        _header = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
        }
        if headers:
            _header.update(headers)
        if 'data' not in kwargs:
            _header['Content-Type'] = 'application/json'
        response = requests.request(method, url, headers=_header, **kwargs)
        response.raise_for_status()
        return self._parse(response)

    def _parse(self, response):
        if 'application/json' in response.headers['Content-Type']:
            r = response.json()
        else:
            r = response.content
        return r
