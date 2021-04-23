import asyncio
import time
from typing import List, Optional

import aiofiles

from nazurin.config import NAZURIN_DATA, STORAGE_DIR, env
from nazurin.database import Database
from nazurin.models import File
from nazurin.utils import Request, logger

OD_FOLDER = STORAGE_DIR
OD_CLIENT = env.str('OD_CLIENT')
OD_SECRET = env.str('OD_SECRET')
OD_RF_TOKEN = env.str('OD_RF_TOKEN')  # Refresh token for first-time auth
OD_DOCUMENT = 'onedrive'

class OneDrive(object):
    """OneDrive driver."""
    db = Database().driver()
    collection = db.collection(NAZURIN_DATA)
    document = collection.document(OD_DOCUMENT)

    access_token = None
    refresh_token = None
    expires_at = 0
    folder_id = None

    async def upload(self, file: File):
        # https://docs.microsoft.com/zh-cn/graph/api/driveitem-createuploadsession?view=graph-rest-1.0
        # create drive item
        create_file_url = 'https://graph.microsoft.com/v1.0/me/drive/items/{parent_id}/children'.format(
            parent_id=self.folder_id)
        size = await file.size()
        body = {
            "name": file.name,
            "size": size,
            "file": {},
            "@microsoft.graph.conflictBehavior": "replace"
        }
        response = await self._request('POST', create_file_url, json=body)
        # create upload session
        create_session_url = 'https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/createUploadSession'.format(
            item_id=response['id'])
        response = await self._request('POST', create_session_url)
        # upload
        headers = {
            'Content-Range': 'bytes 0-{end}/{size}'.format(end=size - 1,
                                                           size=size)
        }
        async with aiofiles.open(file.path, mode='rb') as data:
            await self._request('PUT',
                                response['uploadUrl'],
                                headers=headers,
                                data=await data.read())

    async def store(self, files: List[File]):
        await self.requireAuth()
        if not self.folder_id:
            await self.getDestination()

        tasks = [self.upload(file) for file in files]
        await asyncio.gather(*tasks)

    async def findFolder(self, name: str) -> Optional[str]:
        await self.requireAuth()
        # https://docs.microsoft.com/zh-cn/graph/api/driveitem-list-children?view=graph-rest-1.0&tabs=http
        url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
        folders = dict(await self._request('GET', url))
        folders = folders.get('value')
        for folder in folders:
            if folder['name'] == name:
                return folder['id']
        return None

    async def createFolder(self, name: str) -> str:
        await self.requireAuth()
        # https://docs.microsoft.com/zh-cn/graph/api/driveitem-post-children?view=graph-rest-1.0&tabs=http
        url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
        body = {"name": name, "folder": {}}
        result = await self._request('POST', url, json=body)
        return result['id']

    async def requireAuth(self):
        # https://docs.microsoft.com/zh-cn/azure/active-directory/develop/v2-oauth2-auth-code-flow
        if self.access_token and self.expires_at > time.time():
            # Logged in, access_token not expired
            return

        credentials = await self.document.get()
        if credentials:
            self.refresh_token = credentials['refresh_token']
            if 'folder_id' in credentials.keys():
                self.folder_id = credentials['folder_id']
            if credentials['expires_at'] > time.time():
                self.access_token = credentials['access_token']
                self.expires_at = credentials['expires_at']
                logger.info('OneDrive logged in through cached tokens')
            else:
                await self.auth()  # Refresh access_token
        else:
            # Database should be initialized
            self.refresh_token = OD_RF_TOKEN
            await self.auth(initialize=True)

    async def auth(self, initialize=False):
        # https://docs.microsoft.com/zh-cn/azure/active-directory/develop/v2-oauth2-auth-code-flow
        url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        data = {
            'client_id': OD_CLIENT,
            'client_secret': OD_SECRET,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        async with Request() as request:
            async with request.post(url, data=data) as response:
                response = await response.json()
        self.access_token = response['access_token']
        self.refresh_token = response['refresh_token']
        self.expires_at = time.time() + response['expires_in']
        credentials = {
            'access_token': response['access_token'],
            'refresh_token': response['refresh_token'],
            'expires_at': self.expires_at
        }
        if initialize:
            await self.collection.insert(OD_DOCUMENT, credentials)
            logger.info('OneDrive logged in')
        else:
            await self.document.update(credentials)
            logger.info('OneDrive access token updated')

    async def getDestination(self):
        # Try to find the folder and its id
        self.folder_id = await self.findFolder(OD_FOLDER)
        # Not found, create a new folder
        if not self.folder_id:
            self.folder_id = await self.createFolder(OD_FOLDER)
        await self.document.update({'folder_id': self.folder_id})
        logger.info('OneDrive folder ID cached')

    async def _request(self, method, url, headers=None, **kwargs):
        # make a request with access token
        _headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
        }
        if headers:
            _headers.update(headers)
        if 'data' not in kwargs:
            _headers['Content-Type'] = 'application/json'
        async with Request(headers=_headers) as session:
            async with session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                if 'application/json' in response.headers['Content-Type']:
                    return await response.json()
                return await response.text()
