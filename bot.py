import shutil
import traceback
from config import *
from utils import *
from pixiv import *
from twitter import *
from danbooru import *
from meganz import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async

papi = Pixiv()
mapi = Mega()
tapi = Twitter()
dapi = Danbooru()

@run_async
def start(update, context):
    #Send a message when the command /start is issued.
    update.message.reply_text('Hi!')
@run_async
@typing
def ping(update, context):
    update.message.reply_text('pong!')
@run_async
@typing
def help(update, context):
    update.message.reply_text('''
    This is ***REMOVED*** 's personal bot, used for collecting Pixiv and Twitter images.
    Commands:
    /pixiv <id> - view pixiv artwork
    /pixiv_download <id> - download pixiv artwork
    /bookmark <id> - bookmark pixiv artwork(ADMIN ONLY)
    PS: Send Pixiv/Twitter URL to download image(s)
    ''')
@run_async
def pixiv(update, context):
    message = update.message
    try:
        # args[0] should contain the queried artwork id
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid artwork id!')
            return
        is_admin = message.from_user.id == ADMIN_ID
        imgs, details = papi.artworkDetail(id, is_admin)
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /pixiv <artwork_id>')
    except PixivError as error:
        message.reply_text(error.reason)
@run_async
def pixiv_download(update, context):
    message = update.message
    try:
        # args[0] should contain the queried artwork id
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid artwork id!')
            return
        imgs = papi.downloadArtwork(id=id)
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /pixiv_download <artwork_id>')
    except PixivError as error:
        message.reply_text(error.reason)
@run_async
def danbooru(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id <= 0:
            message.reply_text('Invalid post id!')
            return
        imgs, details = dapi.view(id)
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /danbooru <post_id>')
@run_async
def danbooru_download(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id <= 0:
            message.reply_text('Invalid post id!')
            return
        imgs = dapi.download(id)
        print('downloaded')
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /danbooru_download <post_id>')
@run_async
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
    logger.info('Gallery update: "%s"', src)
    # Perform action
    if user_id == ADMIN_ID:
        # Forward to gallery & Save to album
        bot.forwardMessage(GALLERY, chat_id, message_id)
        chat_id = ALBUM
        message_id = None # No need to reply to message
        is_admin = True
    else:
        # Reply directly to chat
        is_admin = False
    try:
        if src['type'] == 'pixiv':
            if is_admin:
                papi.addBookmark(src['id'])
            imgs = papi.downloadArtwork(id=src['id'])
        elif src['type'] == 'twitter':
            imgs = tapi.download(src['url'])
        elif src['type'] == 'danbooru':
            imgs = dapi.download(src['id'])

        sendDocuments(update, context, imgs, chat_id=chat_id)
        if is_admin:
            # Upload to MEGA
            mapi.upload(imgs)
            logger.info('Uploaded to MEGA')
        message.reply_text('Done!')
    except PixivError as error:
        message.reply_text(error.reason)
def pixiv_bookmark(update, context):
    message = update.message
    try:
        # args[0] should contain the queried artwork id
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid artwork id!')
            return
        papi.addBookmark(id)
        message.reply_text('Done!')
    except (IndexError, ValueError):
        message.reply_text('Usage: /bookmark <artwork_id>')
    except PixivError as error:
        message.reply_text(error.reason)
def clear_downloads(update, context):
    message = update.message
    try:
        shutil.rmtree('./downloads')
        message.reply_text("downloads directory cleared successfully.")
    except PermissionError:
        message.reply_text("Permission denied.") 
    except OSError as error:
        message.reply_text(error.strerror)

def error(update, context):
    logger.error('Update "%s" caused error "%s"', update, context.error)
    traceback.print_exc()

def main():
    urlFilter = Filters.entity('url') | Filters.entity('text_link') | Filters.caption_entity('url') | Filters.caption_entity('text_link')

    # Set up the Updater
    updater = Updater(TOKEN, workers=16, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('ping', ping))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('pixiv', pixiv, pass_args=True))
    dp.add_handler(CommandHandler('pixiv_download', pixiv_download, pass_args=True))
    dp.add_handler(CommandHandler('bookmark', pixiv_bookmark, Filters.user(user_id=ADMIN_ID), pass_args=True))
    dp.add_handler(CommandHandler('danbooru', danbooru, pass_args=True))
    dp.add_handler(CommandHandler('danbooru_download', danbooru_download, pass_args=True))
    dp.add_handler(CommandHandler('clear_downloads', clear_downloads, Filters.user(user_id=ADMIN_ID), pass_args=True))
    dp.add_handler(MessageHandler(urlFilter & (~ Filters.update.channel_posts), gallery_update, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    papi.login()
    if ENV == 'production':
        # Webhook mode
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
        updater.bot.setWebhook("https://***REMOVED***.herokuapp.com/" + TOKEN)
        logger.info('Set webhook')
    else:
        # Polling mode
        updater.start_polling()
        print('Started polling')

    updater.idle()

if __name__ == '__main__':
    main()