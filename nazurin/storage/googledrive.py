import asyncio
import json
from pathlib import PurePath
from typing import Awaitable, Callable, List, Optional

from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive as GDrive
from pydrive2.drive import GoogleDriveFile

from nazurin.config import MAX_PARALLEL_UPLOAD, STORAGE_DIR, env
from nazurin.models import File
from nazurin.utils import logger
from nazurin.utils.decorators import Cache, async_wrap
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import run_in_pool

GD_FOLDER = env.str("GD_FOLDER")
GD_CREDENTIALS = env.str(
    "GD_CREDENTIALS",
    default=env.str("GOOGLE_APPLICATION_CREDENTIALS"),
)
FOLDER_MIME = "application/vnd.google-apps.folder"


class GoogleDrive:
    """Google Drive driver."""

    drive = GDrive()
    create_file: Callable[[dict], Awaitable[GoogleDriveFile]] = async_wrap(
        drive.CreateFile,
    )

    def __init__(self):
        """Initialize and log in."""
        self.auth()

    @staticmethod
    def auth():
        gauth = GoogleAuth()
        scope = ["https://www.googleapis.com/auth/drive"]
        gauth.auth_method = "service"
        if GD_CREDENTIALS:
            if GD_CREDENTIALS.startswith("{"):
                credentials = json.loads(GD_CREDENTIALS)
                gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                    credentials,
                    scope,
                )
            else:
                gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    GD_CREDENTIALS,
                    scope,
                )
        else:
            raise NazurinError("Credentials not found for Google Drive storage.")
        GoogleDrive.drive.auth = gauth

    @staticmethod
    async def upload(file: File, folders: Optional[dict] = None):
        # Compute relative path to STORAGE_DIR, which is GD_FOLDER
        path = file.destination.relative_to(STORAGE_DIR).as_posix()
        parent = folders[path] if folders else await GoogleDrive.create_folders(path)
        metadata = {"title": file.name, "parents": [{"id": parent}]}
        f = await GoogleDrive.create_file(metadata)
        f.SetContentFile(file.path)
        f.Upload()

    async def store(self, files: List[File]):
        # Create necessary folders in advance
        destinations = {
            # Compute relative path to STORAGE_DIR, which is GD_FOLDER
            file.destination.relative_to(STORAGE_DIR).as_posix()
            for file in files
        }
        tasks = [self.create_folders(destination) for destination in destinations]
        logger.info("Creating folders: {}", destinations)
        folder_ids = await asyncio.gather(*tasks)
        folders = dict(zip(destinations, folder_ids))

        tasks = [self.upload(item, folders) for item in files]
        await run_in_pool(tasks, MAX_PARALLEL_UPLOAD)

    @staticmethod
    @Cache.lru()
    @async_wrap
    def find_folder(name: str, parent: Optional[str] = None) -> str:
        query = {
            "q": f"mimeType='{FOLDER_MIME}' and "
            f"title='{name}' and "
            f"'{parent or GD_FOLDER}' in parents",
            "spaces": "drive",
        }
        result = GoogleDrive.drive.ListFile(query).GetList()
        if not result:
            return None
        return result[0].get("id")

    @staticmethod
    async def create_folder(name: str, parent: Optional[str] = None) -> str:
        metadata = {
            "title": name,
            "mimeType": FOLDER_MIME,
            "parents": [{"id": parent or GD_FOLDER}],
        }
        folder = await GoogleDrive.create_file(metadata)
        folder.Upload()
        return folder.get("id")

    @staticmethod
    async def create_folders(path: str, parent: Optional[str] = None) -> str:
        """
        Create folders recursively.

        :param path: Path to create
        :param parent: Parent folder id
        """

        current = parent or GD_FOLDER
        for segment in PurePath(path).parts:
            folder = await GoogleDrive.find_folder(segment, current)
            if not folder:
                folder = await GoogleDrive.create_folder(segment, current)
                # Since `find_folder` cached return value `None`
                # and Google Drive allows duplicate folder names,
                # we need to invalidate the cache
                # to avoid duplicate folders being created.
                GoogleDrive.find_folder.invalidate(segment, current)
            current = folder
        return current
