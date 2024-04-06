import asyncio
import os
import pathlib
import time
from typing import List, Optional
from urllib.parse import quote

from humanize import naturalsize

from nazurin.config import MAX_PARALLEL_UPLOAD, NAZURIN_DATA, STORAGE_DIR, env
from nazurin.database import Database
from nazurin.models import File
from nazurin.utils import Request, logger
from nazurin.utils.decorators import Cache, network_retry
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import read_by_chunks, run_in_pool, sanitize_path

OD_FOLDER = STORAGE_DIR
OD_CLIENT = env.str("OD_CLIENT")
OD_SECRET = env.str("OD_SECRET")
OD_RF_TOKEN = env.str("OD_RF_TOKEN")  # Refresh token for first-time auth
OD_DOCUMENT = "onedrive"

BASE_URL = "https://graph.microsoft.com/v1.0"
# Must be a multiple of 320 KB
UPLOAD_CHUNK_SIZE = 16 * 320 * 1024  # 5MB


class OneDrive:
    """OneDrive driver."""

    db = Database().driver()
    collection = db.collection(NAZURIN_DATA)
    document = collection.document(OD_DOCUMENT)

    access_token = None
    refresh_token = None
    expires_at = 0
    folder_id = None

    async def upload(self, file: File):
        """
        Resumable multipart upload.
        Docs:\
        https://docs.microsoft.com/zh-cn/graph/api/driveitem-createuploadsession?view=graph-rest-1.0
        """

        # create upload session
        logger.info("Creating upload session...")
        body = {
            "item": {
                "@microsoft.graph.conflictBehavior": "replace",
            },
        }
        path = self.encode_path(pathlib.Path(file.destination, file.name))
        create_session_url = (
            f"{BASE_URL}/me/drive/items/root:{path}:/createUploadSession"
        )
        response = await self._request("POST", create_session_url, json=body)
        # upload
        await self.stream_upload(file, response["uploadUrl"])

    async def store(self, files: List[File]):
        await self.require_auth()

        # Create necessary folders in advance
        destinations = {file.destination for file in files}
        tasks = [self.ensure_existence(destination) for destination in destinations]
        logger.info("Creating folders: {}", destinations)
        await asyncio.gather(*tasks)

        tasks = [self.upload(file) for file in files]
        await run_in_pool(tasks, MAX_PARALLEL_UPLOAD)

    @network_retry
    async def find_folder(self, name: str) -> Optional[str]:
        await self.require_auth()
        # https://docs.microsoft.com/zh-cn/graph/api/driveitem-list-children?view=graph-rest-1.0&tabs=http
        url = f"{BASE_URL}/me/drive/root/children"
        folders = dict(await self._request("GET", url))
        folders = folders.get("value")
        for folder in folders:
            if folder["name"] == name:
                return folder["id"]
        return None

    @network_retry
    async def create_folder(self, name: str, parent_id: str = "root") -> str:
        """
        Create a folder in the given parent folder and return the ID of created folder.
        If `parent_id` is not specified, the folder will be created at the root.

        Docs:\
        https://docs.microsoft.com/zh-cn/graph/api/driveitem-post-children?view=graph-rest-1.0&tabs=http
        """

        await self.require_auth()
        url = f"{BASE_URL}/me/drive/items/{parent_id}/children"
        body = {"name": name, "folder": {}}
        result = await self._request("POST", url, json=body)
        return result["id"]

    @network_retry
    @Cache.lru()
    async def ensure_existence(self, path: str):
        """
        Ensure the given path exists under `OD_FOLDER`
        and return the ID of the innermost folder.
        If not, create the necessary folders.
        """

        path = self.encode_path(path)
        await self.require_auth()
        # Hack to create nested folders in one go
        # https://stackoverflow.com/questions/56479865/creating-nested-folders-in-one-go-onedrive-api
        url = f"{BASE_URL}/me/drive/items/root:{path}"
        body = {"folder": {}, "@microsoft.graph.conflictBehavior": "replace"}
        result = await self._request("PATCH", url, json=body)
        return result["id"]

    async def require_auth(self):
        # https://docs.microsoft.com/zh-cn/azure/active-directory/develop/v2-oauth2-auth-code-flow
        if self.access_token and self.expires_at > time.time():
            # Logged in, access_token not expired
            return

        credentials = await self.document.get()
        if credentials:
            self.refresh_token = credentials["refresh_token"]
            if "folder_id" in credentials:
                self.folder_id = credentials["folder_id"]
            if credentials["expires_at"] > time.time():
                self.access_token = credentials["access_token"]
                self.expires_at = credentials["expires_at"]
                logger.info("OneDrive logged in through cached tokens")
            else:
                await self.auth()  # Refresh access_token
        else:
            # Database should be initialized
            self.refresh_token = OD_RF_TOKEN
            await self.auth(initialize=True)

    @network_retry
    async def auth(self, *, initialize=False):
        # https://docs.microsoft.com/zh-cn/azure/active-directory/develop/v2-oauth2-auth-code-flow
        url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        data = {
            "client_id": OD_CLIENT,
            "client_secret": OD_SECRET,
            "refresh_token": self.refresh_token or OD_RF_TOKEN,
            "grant_type": "refresh_token",
        }
        async with Request() as request, request.post(url, data=data) as response:
            response_json = await response.json()
            if "error" in response_json:
                logger.error(response_json)
                raise NazurinError(
                    f"OneDrive authorization error: {response_json['error_description']}",
                )
            self.access_token = response_json["access_token"]
            self.refresh_token = response_json["refresh_token"]
            self.expires_at = time.time() + response_json["expires_in"]
        credentials = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
        }
        if initialize:
            await self.collection.insert(OD_DOCUMENT, credentials)
            logger.info("OneDrive logged in")
        else:
            await self.document.update(credentials)
            logger.info("OneDrive access token updated")

    async def get_destination(self):
        if self.folder_id:
            return
        # Try to find the folder and its id
        self.folder_id = await self.find_folder(OD_FOLDER)
        # Not found, create a new folder
        if not self.folder_id:
            self.folder_id = await self.create_folder(OD_FOLDER)
        await self.document.update({"folder_id": self.folder_id})
        logger.info("OneDrive folder ID cached")

    @network_retry
    async def _request(self, method, url, headers=None, **kwargs):
        # make a request with access token
        _headers = self.with_credentials(headers)
        _headers["Content-Type"] = "application/json"
        async with Request(headers=_headers) as session, session.request(
            method,
            url,
            **kwargs,
        ) as response:
            if not response.ok:
                logger.error(await response.text())
            response.raise_for_status()
            if "application/json" in response.headers["Content-Type"]:
                return await response.json()
            return await response.text()

    async def stream_upload(self, file: File, url: str):
        @network_retry
        async def upload_chunk(url: str, chunk: bytes):
            async with session.put(url, data=chunk) as response:
                if not response.ok:
                    logger.error(await response.text())
                response.raise_for_status()

        headers = self.with_credentials()
        range_start = 0
        total_size = await file.size()
        total_size_str = naturalsize(total_size, binary=True)
        logger.info(
            "[File {}] Start upload, total size: {}...",
            file.name,
            total_size_str,
        )

        async with Request(headers=headers) as session:
            async for chunk in read_by_chunks(file.path, UPLOAD_CHUNK_SIZE):
                content_length = len(chunk)
                range_end = range_start + content_length - 1
                session.headers.update({"Content-Length": str(content_length)})
                session.headers.update(
                    {"Content-Range": f"bytes {range_start}-{range_end}/{total_size}"},
                )
                await upload_chunk(url, chunk)
                range_start += content_length
                logger.info(
                    "[File {}] Uploaded {} / {}",
                    file.name,
                    naturalsize(range_start, binary=True),
                    total_size_str,
                )
        logger.info("[File {}] Upload completed", file.name)

    def with_credentials(self, headers: Optional[dict] = None) -> dict:
        """
        Add credentials to the request header.
        """

        _headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + self.access_token,
        }
        if headers:
            _headers.update(headers)
        return _headers

    @staticmethod
    def encode_path(_path: os.PathLike) -> str:
        """
        Sanitize and encode the given path to a valid URL to address drive items.

        Docs: https://learn.microsoft.com/en-us/graph/onedrive-addressing-driveitems
        """

        def sanitize(segment: str) -> str:
            if segment.endswith("."):
                segment = segment[:-1]
            if segment.startswith("~"):
                segment = segment[1:]
            if len(segment) == 0:
                segment = "_"
            return segment

        path = sanitize_path(_path, sanitize)
        if not path.root:
            path = "/" / path
        return quote(path.as_posix())
