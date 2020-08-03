from shutil import copyfileobj
from os import path, makedirs
from requests import get
import re
from functools import wraps
from config import *
from telegram import ChatAction, InputMediaPhoto

def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func

    return decorator

typing = send_action(ChatAction.TYPING)
uploading_video = send_action(ChatAction.UPLOAD_VIDEO)
uploading_photo = send_action(ChatAction.UPLOAD_PHOTO)
uploading_document = send_action(ChatAction.UPLOAD_DOCUMENT)

@uploading_photo
def sendPhotos(update, context, imgs, details=dict()):
    bot = context.bot
    message = update.message
    chat_id = message.chat_id
    message_id = message.message_id
    media = list()
    if len(imgs) > 10:
        imgs = imgs[:9]
        message.reply_text('Notice: Too many pages, sending only 10 of them' )
    caption = str()
    for key, value in details.items():
        caption += str(key) + ': ' + str(value) + '\n'
    for img in imgs:
        media.append(InputMediaPhoto(img['url'], caption, 'HTML'))
    bot.sendMediaGroup(chat_id, media, reply_to_message_id=message_id)
@uploading_document
def sendDocuments(update, context, imgs, chat_id=None):
    bot = context.bot
    message_id = update.message.message_id
    if not chat_id:
        chat_id = update.message.chat_id
    else:
        message_id = None # Sending to channel, no message to reply
    for img in imgs:
        bot.sendDocument(chat_id, open(DOWNLOAD_DIR + img['name'], 'rb'), filename=img['name'], reply_to_message_id=message_id)

def handleBadRequest(update, context, error):
    if 'Wrong file identifier/http url' in error.message:
        update.message.reply_text('Failed to send image as photo, maybe the size is too big, please consider using download option instead.', quote=True)
    else:
        raise error

def downloadImages(imgs, headers={}):
    headers['User-Agent'] = UA
    if not path.exists(DOWNLOAD_DIR):
        makedirs(DOWNLOAD_DIR)
    for img in imgs:
        downloadImage(img['url'], img['name'], headers)

def downloadImage(url, path, headers={}):
    if not os.path.exists(DOWNLOAD_DIR + path):
        response = get(url, headers=headers, stream=True).raw
        with open(DOWNLOAD_DIR + path, 'wb') as f:
            copyfileobj(response, f)

class NazurinError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = str(msg)

    def __str__(self):
        return self.msg