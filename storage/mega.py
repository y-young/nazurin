# -*- coding: utf-8 -*-
import os
from config import *
from database import Database
from mega import Mega as mega
from mega.errors import RequestError

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
            Mega.collection.insert(MEGA_DOCUMENT, {
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
            else: # Initialize database
                self.login(initialize=True)
        if not Mega.destination:
            self.getDestination()

    def getDestination(self):
        Mega.destination = Mega.api.find(STORAGE_DIR, exclude_deleted=True)[0]
        Mega.document.update({
            'destination': Mega.destination
        })
        logger.info('MEGA destination cached')

    def store(self, files):
        self.requireAuth()
        for item in files:
            self.call(Mega.api.upload, DOWNLOAD_DIR + item['name'], Mega.destination)

    def call(self, func, *args):
        try:
            func(*args)
        except RequestError as error:
            # mega.errors.RequestError: ESID, Invalid or expired user session, please relogin
            if 'relogin' in error.message:
                logger.info(error)
                Mega.api.sid = None
                self.login()
            func(*args)
