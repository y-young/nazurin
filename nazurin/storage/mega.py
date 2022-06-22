# -*- coding: utf-8 -*-
import asyncio
from typing import List

from mega import Mega as mega
from mega.errors import RequestError

from nazurin.config import NAZURIN_DATA, STORAGE_DIR, env
from nazurin.database import Database
from nazurin.models import File
from nazurin.utils import logger
from nazurin.utils.decorators import async_wrap

MEGA_USER = env.str('MEGA_USER')
MEGA_PASS = env.str('MEGA_PASS')
MEGA_DOCUMENT = 'mega'

class Mega:
    api = mega()
    db = Database().driver()
    collection = db.collection(NAZURIN_DATA)
    document = collection.document(MEGA_DOCUMENT)
    destination = None

    api_login = async_wrap(api.login)
    api_upload = async_wrap(api.upload)
    create_folder = async_wrap(api.create_folder)
    find_folder = async_wrap(api.find)

    async def login(self, initialize=False):
        await Mega.api_login(MEGA_USER, MEGA_PASS)
        if initialize:
            await Mega.collection.insert(
                MEGA_DOCUMENT, {
                    'sid': Mega.api.sid,
                    'master_key': list(Mega.api.master_key),
                    'root_id': Mega.api.root_id
                })
        else:
            await Mega.document.update({
                'sid': Mega.api.sid,
                'master_key': list(Mega.api.master_key),
                'root_id': Mega.api.root_id
            })
        logger.info('MEGA tokens cached')

    async def require_auth(self):
        if not Mega.api.sid:
            tokens = await Mega.document.get()
            if tokens and 'sid' in tokens.keys():
                Mega.api.sid = tokens['sid']
                Mega.api.master_key = tuple(tokens['master_key'])
                Mega.api.root_id = tokens['root_id']
                logger.info('MEGA logged in through cached tokens')
                if 'destination' in tokens.keys():
                    Mega.destination = tokens['destination']
                    logger.info('MEGA retrieved destination from cache')
            else:  # Initialize database
                await self.login(initialize=True)
        if not Mega.destination:
            await self.get_destination()

    async def get_destination(self):
        result = await Mega.find_folder(STORAGE_DIR, exclude_deleted=True)
        if result:
            Mega.destination = result[0]
        else:
            result = await Mega.create_folder(STORAGE_DIR)
            Mega.destination = result[STORAGE_DIR]
        await Mega.document.update({'destination': Mega.destination})
        logger.info('MEGA destination cached')

    async def upload(self, file: File):
        while True:
            try:
                await Mega.api_upload(file.path, Mega.destination)
                break
            except RequestError as error:
                # mega.errors.RequestError: ESID, Invalid or expired user session, please relogin
                if 'relogin' in error.message:
                    logger.info(error)
                    Mega.api.sid = None
                    await self.login()

    async def store(self, files: List[File]):
        await self.require_auth()
        tasks = [self.upload(file) for file in files]
        await asyncio.gather(*tasks)
