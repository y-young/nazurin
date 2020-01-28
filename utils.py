import re
from functools import wraps
from telegram import ChatAction

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

def match_url(url):
    if 'pixiv' in url:
        pattern = re.compile('[0-9]+')
        match = re.findall(pattern, url)
        return {'type': 'pixiv', 'id': match[0]}
    elif 'twitter' in url:
        return {'type': 'twitter', 'url': url}
    else:
        return None