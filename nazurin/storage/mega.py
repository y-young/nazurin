# -*- coding: utf-8 -*-
import asyncio
import os

from mega import Mega as mega
from mega.errors import RequestError

from nazurin.config import NAZURIN_DATA, STORAGE_DIR
from nazurin.database import Database
from nazurin.utils import async_wrap, logger

MEGA_USER = os.environ.get('MEGA_USER')
MEGA_PASS = os.environ.get('MEGA_PASS')
MEGA_DOCUMENT = 'mega'

class Mega(object):
    api = mega()
    db = Database().driver()
    collection = db.collection(NAZURIN_DATA)
    document = collection.document(MEGA_DOCUMENT)
    destination = None

    def login(self, initialize=False):
        Mega.api.login(MEGA_USER, MEGA_PASS)
        if initialize:
            Mega.collection.insert(
                MEGA_DOCUMENT, {
                    'sid': Mega.api.sid,
                    'master_key': list(Mega.api.master_key),
                    'root_id': Mega.api.root_id
                })
        else:
            Mega.document.update({
                'sid': Mega.api.sid,
                'master_key': list(Mega.api.master_key),
                'root_id': Mega.api.root_id
            })
        logger.info('MEGA tokens cached')

    def requireAuth(self):
        if not Mega.api.sid:
            tokens = Mega.document.get()
            if tokens and 'sid' in tokens.keys():
                Mega.api.sid = tokens['sid']
                Mega.api.master_key = tuple(tokens['master_key'])
                Mega.api.root_id = tokens['root_id']
                logger.info('MEGA logged in through cached tokens')
                if 'destination' in tokens.keys():
                    Mega.destination = tokens['destination']
                    logger.info('MEGA retrieved destination from cache')
            else:  # Initialize database
                self.login(initialize=True)
        if not Mega.destination:
            self.getDestination()

    def getDestination(self):
        result = Mega.api.find(STORAGE_DIR, exclude_deleted=True)
        if result:
            Mega.destination = result[0]
        else:
            result = Mega.api.create_folder(STORAGE_DIR)
            Mega.destination = result[STORAGE_DIR]
        Mega.document.update({'destination': Mega.destination})
        logger.info('MEGA destination cached')

    @async_wrap
    def upload(self, file):
        while True:
            try:
                Mega.api.upload(file.path, Mega.destination)
                break
            except RequestError as error:
                # mega.errors.RequestError: ESID, Invalid or expired user session, please relogin
                if 'relogin' in error.message:
                    logger.info(error)
                    Mega.api.sid = None
                    self.login()

    async def store(self, files):
        self.requireAuth()
        tasks = [self.upload(file) for file in files]
        await asyncio.gather(*tasks)
