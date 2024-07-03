import asyncio
from typing import List, Optional

from mega import Mega as MegaBase
from mega.errors import RequestError

from nazurin.config import MAX_PARALLEL_UPLOAD, NAZURIN_DATA, env
from nazurin.database import Database
from nazurin.models import File
from nazurin.utils import logger
from nazurin.utils.decorators import Cache, async_wrap, network_retry
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import run_in_pool

MEGA_USER = env.str("MEGA_USER")
MEGA_PASS = env.str("MEGA_PASS")
MEGA_DOCUMENT = "mega"


class Mega:
    api = MegaBase()
    db = Database().driver()
    collection = db.collection(NAZURIN_DATA)
    document = collection.document(MEGA_DOCUMENT)
    destination = None

    api_login = async_wrap(api.login)
    api_upload = async_wrap(api.upload)
    create_folder = async_wrap(api.create_folder)

    @network_retry
    async def login(self, *, initialize=False):
        await Mega.api_login(MEGA_USER, MEGA_PASS)
        if initialize:
            await Mega.collection.insert(
                MEGA_DOCUMENT,
                {
                    "sid": Mega.api.sid,
                    "master_key": list(Mega.api.master_key),
                    "root_id": Mega.api.root_id,
                },
            )
        else:
            await Mega.document.update(
                {
                    "sid": Mega.api.sid,
                    "master_key": list(Mega.api.master_key),
                    "root_id": Mega.api.root_id,
                },
            )
        logger.info("MEGA tokens cached")

    async def require_auth(self):
        if not Mega.api.sid:
            tokens = await Mega.document.get()
            if tokens and "sid" in tokens:
                Mega.api.sid = tokens["sid"]
                Mega.api.master_key = tuple(tokens["master_key"])
                Mega.api.root_id = tokens["root_id"]
                logger.info("MEGA logged in through cached tokens")
            else:  # Initialize database
                await self.login(initialize=True)

    @network_retry
    async def upload(
        self,
        file: File,
        folders: Optional[dict] = None,
        *,
        retry: bool = False,
    ):
        path = file.destination.as_posix()
        try:
            destination = (
                folders[path] if folders else await self.ensure_existence(path)
            )
            await Mega.api_upload(file.path, destination)
        except RequestError as error:
            # mega.errors.RequestError:
            # ESID, Invalid or expired user session, please relogin
            if "relogin" in error.message and not retry:
                logger.info(error)
                Mega.api.sid = None
                await self.login()
                await self.upload(file, folders, retry=True)

    async def store(self, files: List[File]):
        await self.require_auth()

        # Create necessary folders in advance
        destinations = {file.destination.as_posix() for file in files}
        tasks = [self.ensure_existence(destination) for destination in destinations]
        logger.info("Creating folders: {}", destinations)
        folder_ids = await asyncio.gather(*tasks)
        folders = dict(zip(destinations, folder_ids))

        tasks = [self.upload(file, folders) for file in files]
        await run_in_pool(tasks, MAX_PARALLEL_UPLOAD)

    @network_retry
    @Cache.lru()
    async def ensure_existence(self, path: str) -> str:
        result = await Mega.create_folder(path)
        if result.get(path):
            return result[path]
        raise NazurinError("Failed to create folder: " + path)
