from requests.adapters import HTTPAdapter
from mimetypes import guess_type
from shutil import copyfileobj
from functools import wraps
from pathlib import Path
from html import escape
from time import sleep
import requests
import logging
import re
import os
from config import DOWNLOAD_DIR, UA, RETRIES
from telegram import ChatAction, InputMediaPhoto
from telegram.error import RetryAfter

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('bot')

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
def sendPhotos(update, context, imgs, details=None):
    if details is None:
        details = dict()
    bot = context.bot
    message = update.message
    chat_id = message.chat_id
    message_id = message.message_id
    media = list()
    if len(imgs) > 10:
        imgs = imgs[:10]
        message.reply_text('Notice: Too many pages, sending only 10 of them' )
    caption = str()
    for key, value in details.items():
        caption += str(key) + ': ' + str(value) + '\n'
    if len(caption) > 1024:
        caption = caption[:1024]
        message.reply_text('Notice: Caption too long, trimmed')
    caption = escape(caption, quote=False)

    for img in imgs:
        url = img['url'].split('?')[0] # remove query string
        filetype = str(guess_type(url)[0])
        if filetype.startswith('image'):
            url = chooseUrl(img)
            media.append(InputMediaPhoto(url, parse_mode='HTML'))
        else:
            message.reply_text('File is not image, try download option.')
            return
    media[0].caption = caption
    while True:
        try:
            bot.sendMediaGroup(chat_id, media, reply_to_message_id=message_id)
        except RetryAfter as error:
            sleep(error.retry_after)
            continue
        break
@uploading_document
def sendDocuments(update, context, imgs, chat_id=None):
    bot = context.bot
    message_id = update.message.message_id
    if not chat_id:
        chat_id = update.message.chat_id
    else:
        message_id = None # Sending to channel, no message to reply
    for img in imgs:
        while True:
            try:
                bot.sendDocument(chat_id, open(DOWNLOAD_DIR + img['name'], 'rb'), filename=img['name'], reply_to_message_id=message_id)
            except RetryAfter as error:
                sleep(error.retry_after)
                continue
            break

def chooseUrl(img):
    url = img['url']
    if 'size' in img.keys():
        size = img['size']
    else:
        headers = requests.head(url, headers={'Referer': 'https://www.pixiv.net/'}).headers
        if 'Content-Length' in headers.keys():
            size = int(headers['Content-Length'])
        else:
            size = 0
    if size > 5*1024*1024 and 'thumbnail' in img.keys():
        url = img['thumbnail']
        logger.info('Use thumbnail: ' + url)
    return url

def handleBadRequest(update, context, error):
    logger.info('BadRequest exception: ' + str(error))
    if 'Wrong file identifier/http url' in error.message or 'Failed to get http url content' in error.message:
        update.message.reply_text(
            'Failed to send image as photo, maybe the size is too big, '
            'consider using download option or try again.\n'
            f'Error: {error.message}'
        )
    elif 'Group send failed' in error.message:
        update.message.reply_text(
            'Failed to send images because one of them is too large, '
            'consider using download option or try again.\n'
            f'Error: {error.message}'
        )
    else:
        raise error

def downloadImages(imgs, headers=None):
    if headers is None:
        headers = dict()
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    with requests.Session() as session:
        session.headers.update({'User-Agent': UA})
        session.mount('https://', HTTPAdapter(max_retries=RETRIES))
        for img in imgs:
            response = session.get(img['url'], stream=True, timeout=5).raw
            with open(DOWNLOAD_DIR + img['name'], 'wb') as f:
                copyfileobj(response, f)

def sanitizeFilename(name):
    # https://docs.microsoft.com/zh-cn/windows/win32/fileio/naming-a-file
    name = re.sub(r"[\"*/:<>?\\|]+", '_', name) # reserved characters
    name = re.sub(r"[\t\n\r\f\v]+", ' ', name)
    name = re.sub(r"\u202E|\u200E|\u200F", '', name) # RTL marks
    filename, ext = os.path.splitext(name)
    filename = filename.strip()
    if Path(filename).is_reserved():
        filename = '_' + filename
    name = filename + ext
    if len(name) > 255:
        name = filename[:255 - len(ext)] + ext
    return name

class NazurinError(Exception):
    def __init__(self, msg):
        """Initialize with error message."""
        super().__init__(msg)
        self.msg = str(msg)

    def __str__(self):
        """Returns the string representation of this exception."""
        return self.msg