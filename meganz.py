import os
from config import *
from mega import Mega as mega

class Mega(object):
    api = mega()
    destination = None

    def login(self):
        self.api.login(MEGA_USER, MEGA_PASS)

    def requireAuth(self):
        if not self.api.sid:
            self.login()
        if not self.destination:
            self.destination = self.api.find(UPLOAD_DIR)[0]

    def upload(self, imgs):
        self.requireAuth()
        for img in imgs:
            self.api.upload(DOWNLOAD_DIR + img['name'], self.destination)
