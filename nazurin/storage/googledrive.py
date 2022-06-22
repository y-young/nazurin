import asyncio
import json
from typing import List

from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive as GDrive

from nazurin.config import env
from nazurin.models import File
from nazurin.utils.decorators import async_wrap
from nazurin.utils.exceptions import NazurinError

GD_FOLDER = env.str('GD_FOLDER')
GD_CREDENTIALS = env.str('GD_CREDENTIALS',
                         default=env.str('GOOGLE_APPLICATION_CREDENTIALS'))

class GoogleDrive:
    """Google Drive driver."""
    drive = None

    def __init__(self):
        """Initialize and log in."""
        self.auth()

    @staticmethod
    def auth():
        if GoogleDrive.drive:
            return
        gauth = GoogleAuth()
        scope = ['https://www.googleapis.com/auth/drive']
        gauth.auth_method = 'service'
        if GD_CREDENTIALS:
            if GD_CREDENTIALS.startswith('{'):
                credentials = json.loads(GD_CREDENTIALS)
                gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                    credentials, scope)
            else:
                gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    GD_CREDENTIALS, scope)
        else:
            raise NazurinError(
                'Credentials not found for Google Drive storage.')
        GoogleDrive.drive = GDrive(gauth)

    @staticmethod
    @async_wrap
    def upload(file: File):
        metadata = {'title': file.name, 'parents': [{'id': GD_FOLDER}]}
        f = GoogleDrive.drive.CreateFile(metadata)
        f.SetContentFile(file.path)
        f.Upload()

    async def store(self, files: List[File]):
        tasks = [self.upload(item) for item in files]
        await asyncio.gather(*tasks)

    @staticmethod
    def find_folder(name: str) -> str:
        query = {
            'q': "mimeType='application/vnd.google-apps.folder' and title='" +
            name + "'",
            'spaces': 'drive'
        }
        result = GoogleDrive.drive.ListFile(query).GetList()
        return result[0].get('id')

    @staticmethod
    def create_folder(name: str) -> str:
        metadata = {
            'title': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [{
                'id': GD_FOLDER
            }]
        }
        folder = GoogleDrive.drive.CreateFile(metadata)
        folder.Upload()
        return folder.get('id')
