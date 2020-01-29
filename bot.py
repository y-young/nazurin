import logging
import os
import traceback
from utils import *
from pixiv import *
from twitter import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InputMediaPhoto, ChatAction

papi = Pixiv()
ALBUM = int(os.environ.get('ALBUM'))
GALLERY = int(os.environ.get('GALLERY'))
ADMIN_ID = int(os.environ.get('ADMIN_ID'))
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update, context):
    #Send a message when the command /start is issued.
    update.message.reply_text('Hi!')
@typing
def ping(update, context):
    update.message.reply_text('pong!')
@uploading_photo
def pixiv(update, context):
    global papi
    try:
        # args[0] should contain the queried artwork id
        id = int(context.args[0])
        if id < 0:
            update.message.reply_text('Invalid artwork id!')
            return
        bot = context.bot
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        imgs, details = papi.artworkDetail(id)
        caption = str()
        for key, value in details.items():
            caption += key + ': ' + value + '\n'
        media = list()
        for img in imgs:
            media.append(InputMediaPhoto(img['url'], caption, 'HTML'))
        bot.sendMediaGroup(chat_id, media, reply_to_message_id=message_id)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /pixiv <artwork_id>')
    except PixivError as error:
        update.message.reply_text(error.reason)
@uploading_document
def pixiv_download(update, context):
    global papi
    try:
        # args[0] should contain the queried artwork id
        id = int(context.args[0])
        if id < 0:
            update.message.reply_text('Invalid artwork id!')
            return
        sendPixivDocument(context, id, update=update)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /pixiv_download <artwork_id>')
def gallery_update(update, context):
    message = update.message
    message_id = message.message_id
    chat_id = message.chat_id
    user_id = message.from_user.id
    bot = context.bot
    src = None
    # Match URL
    if message.entities:
        entities = message.entities
        text = message.text
    elif message.caption_entities:
        entities = message.caption_entities
        text = message.caption
    else:
        return
    for item in entities:
        if item.type == 'text_link':
            src = match_url(item.url)
        elif item.type == 'url':
            offset = item.offset
            length = item.length
            src = match_url(text[offset:offset + length])
    if not src:
        return
    logger.info('gallery update: "%s"', src)
    # Perform action
    if user_id == ADMIN_ID:
        # Forward to gallery & Save to album
        bot.forwardMessage(GALLERY, chat_id, message_id)
        chat_id = ALBUM
        message_id = None # No need to reply to message
    else:
        # Reply directly to chat
        bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_DOCUMENT)
    if src['type'] == 'pixiv':
        sendPixivDocument(context, src['id'], chat_id=chat_id)
    elif src['type'] == 'twitter':
        imgs = twitter_download(src['url'])
        for img in imgs:
            bot.sendDocument(chat_id, open('./downloads/' + img['name'], 'rb'), filename=img['name'], reply_to_message_id=message_id)

def error(update, context):
    logger.error('Update "%s" caused error "%s"', update, context.error)
    traceback.print_exc()

def sendPixivDocument(context, id, update=None, chat_id=None):
    bot = context.bot
    if update:
        chat_id = update.message.chat_id
        message_id = update.message.message_id
    else:
        message_id = None
    try:
        imgs = papi.downloadArtwork(id=id)
        for img in imgs:
            bot.sendDocument(chat_id, open('./downloads/' + img['name'], 'rb'), filename=img['name'], reply_to_message_id=message_id)
    except PixivError as error:
        update.message.reply_text(error.reason)
def main():
    global api
    ENV = os.environ.get('ENV')
    TOKEN = os.environ.get('TOKEN')
    # Port is given by Heroku
    PORT = int(os.environ.get('PORT', '8443'))
    PIXIV_USER = os.environ.get('PIXIV_USER')
    PIXIV_PASS = os.environ.get('PIXIV_PASS')
    urlFilter = Filters.entity('url') | Filters.entity('text_link') | Filters.caption_entity('url') | Filters.caption_entity('text_link')

    # Set up the Updater
    updater = Updater(TOKEN, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('ping', ping))
    dp.add_handler(CommandHandler('pixiv', pixiv, Filters.user(user_id=ADMIN_ID), pass_args=True))
    dp.add_handler(CommandHandler('pixiv_download', pixiv_download, Filters.user(user_id=ADMIN_ID), pass_args=True))
    dp.add_handler(MessageHandler(urlFilter, gallery_update, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    if ENV == 'production':
        # Webhook mode
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
        updater.bot.setWebhook("https://***REMOVED***.herokuapp.com/" + TOKEN)
    else:
        # Polling mode
        updater.start_polling()

    papi.login(PIXIV_USER, PIXIV_PASS)
    logger.info('Pixiv logged in successfully')
    updater.idle()

if __name__ == '__main__':
    main()