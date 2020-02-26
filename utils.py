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

def match_url(url):
    id_pattern = re.compile('[0-9]+')
    if 'pixiv' in url:
        match = re.findall(id_pattern, url)
        return {'type': 'pixiv', 'id': match[0]}
    elif 'twitter' in url:
        return {'type': 'twitter', 'url': url}
    elif 'danbooru.donmai.us' in url:
        match = re.findall(id_pattern, url)
        return {'type': 'danbooru', 'id': match[0]}
    elif 'yande.re' in url:
        match = re.findall(id_pattern, url)
        return {'type': 'yandere', 'id': match[0]}
    elif 'konachan.com' in url:
        match = re.findall(id_pattern, url)
        return {'type': 'konachan', 'id': match[0]}
    else:
        return None

def handleBadRequest(update, context, error):
    if 'Wrong file identifier/http url' in error.message:
        update.message.reply_text('Failed to send image as photo, maybe the size is too big, please consider using download option instead.', quote=True)
    else:
        raise error