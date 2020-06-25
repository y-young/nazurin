# -*- coding: utf-8 -*-
import os
from config import *
from database import Firebase
from mega import Mega as mega
from mega.errors import RequestError

class Mega(object):
    def __init__(self):
        self.api = mega()
        self.db = Firebase()
        self.destination = None

    def login(self, initialize=False):
        self.api.login(MEGA_USER, MEGA_PASS)
        if initialize:
            self.db.store(FIREBASE_COLLECION, 'mega', {
                'sid': self.api.sid,
                'master_key': list(self.api.master_key),
                'root_id': self.api.root_id
            })
        else:
            self.db.update(FIREBASE_COLLECION, 'mega', {
                'sid': self.api.sid,
                'master_key': list(self.api.master_key),
                'root_id': self.api.root_id
            })
        logger.info('MEGA tokens cached')

    def requireAuth(self):
        if not self.api.sid:
            tokens = self.db.get(FIREBASE_COLLECION, 'mega')
            if 'sid' in tokens.keys():
                self.api.sid = tokens['sid']
                self.api.master_key = tuple(tokens['master_key'])
                self.api.root_id = tokens['root_id']
                logger.info('MEGA logged in through cached tokens')
                if 'destination' in tokens.keys():
                    self.destination = tokens['destination']
                    logger.info('MEGA retrieved destination from cache')
            else: # Initialize database
                self.login(initialize=True)
        if not self.destination:
            self.getDestination()

    def getDestination(self):
        self.destination = self.api.find(UPLOAD_DIR, exclude_deleted=True)[0]
        self.db.update(FIREBASE_COLLECION, 'mega', {
            'destination': self.destination
        })
        logger.info('MEGA destination cached')

    def upload(self, imgs):
        self.requireAuth()
        for img in imgs:
            self.call(self.api.upload, DOWNLOAD_DIR + img['name'], self.destination)

    def call(self, func, *args):
        try:
            func(*args)
        except RequestError as error:
            # mega.errors.RequestError: ESID, Invalid or expired user session, please relogin
            if 'relogin' in error.message:
                logger.info(error)
                self.api.sid = None
                self.login()
            func(*args)
