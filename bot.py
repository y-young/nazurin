import shutil
import traceback
from config import *
from utils import *
from sites import Twitter
from sites.pixiv import Pixiv, PixivError
from sites.danbooru import Danbooru, DanbooruError
from sites.moebooru import Moebooru, MoebooruError
from meganz import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
from telegram.error import BadRequest

danbooru = Danbooru()
pixiv = Pixiv()
twitter = Twitter()
mega = Mega()

@run_async
def start(update, context):
    update.message.reply_text('Hi!')
@run_async
@typing
def ping(update, context):
    update.message.reply_text('pong!', quote=True)
@run_async
@typing
def help(update, context):
    update.message.reply_text('''
    小さな小さな賢将, can help you collect images from various sites.
    Commands:
    /pixiv <id> - view pixiv artwork
    /pixiv_download <id> - download pixiv artwork
    /danbooru <id> - view danbooru post
    /danbooru_download <id> - download danbooru post
    /yandere <id> - view yandere post
    /yandere_download <id> - download yandere post
    /konachan <id> - view konachan post
    /konachan_download <id> - download konachan post
    /bookmark <id> - bookmark pixiv artwork(ADMIN ONLY)
    PS: Send Pixiv/Danbooru/Yandere/Konachan/Twitter URL to download image(s)
    ''')
@run_async
def pixiv_view(update, context):
    message = update.message
    try:
        # args[0] should contain the queried artwork id
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid artwork id!', quote=True)
            return
        is_admin = message.from_user.id == ADMIN_ID
        imgs, details = pixiv.view(id, is_admin)
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /pixiv <artwork_id>', quote=True)
    except PixivError as error:
        message.reply_text(error.reason, quote=True)
    except BadRequest as error:
        handleBadRequest(update, context, error)
@run_async
def pixiv_download(update, context):
    message = update.message
    try:
        # args[0] should contain the queried artwork id
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid artwork id!', quote=True)
            return
        imgs = pixiv.download(id=id)
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /pixiv_download <artwork_id>', quote=True)
    except PixivError as error:
        message.reply_text(error.reason, quote=True)
@run_async
def danbooru_view(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id <= 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        imgs, details = danbooru.view(id)
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /danbooru <post_id>', quote=True)
    except DanbooruError as error:
        message.reply_text(error.msg, quote=True)
    except BadRequest:
        handleBadRequest(update, context, error)
@run_async
def danbooru_download(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id <= 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        imgs = danbooru.download(id)
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /danbooru_download <post_id>', quote=True)
    except DanbooruError as error:
        message.reply_text(error.msg, quote=True)
@run_async
def yandere_view(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        moebooru = Moebooru('yandere')
        imgs, details = moebooru.view(id)
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /yandere <post_id>', quote=True)
    except BadRequest:
        handleBadRequest(update, context, error)
    except MoebooruError as error:
        message.reply_text(error.msg, quote=True)
@run_async
def yandere_download(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id <= 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        moebooru = Moebooru('yandere')
        imgs = moebooru.download(id)
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /yandere_download <post_id>', quote=True)
    except MoebooruError as error:
        message.reply_text(error.msg, quote=True)
@run_async
def konachan_view(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        moebooru = Moebooru('konachan')
        imgs, details = moebooru.view(id)
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /konachan <post_id>', quote=True)
    except BadRequest:
        handleBadRequest(update, context, error)
    except MoebooruError as error:
        message.reply_text(error.msg, quote=True)
@run_async
def konachan_download(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id <= 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        moebooru = Moebooru('konachan')
        imgs = moebooru.download(id)
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /konachan_download <post_id>', quote=True)
    except MoebooruError as error:
        message.reply_text(error.msg, quote=True)
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
                pixiv.bookmark(src['id'])
            imgs = pixiv.download(id=src['id'])
        elif src['type'] == 'twitter':
            imgs = twitter.download(src['url'])
        elif src['type'] == 'danbooru':
            imgs = danbooru.download(src['id'])
        elif src['type'] in ['yandere', 'konachan']:
            moebooru = Moebooru(src['type'])
            imgs = moebooru.download(src['id'])

        sendDocuments(update, context, imgs, chat_id=chat_id)
        if is_admin:
            # Upload to MEGA
            mega.upload(imgs)
            logger.info('Uploaded to MEGA')
            message.reply_text('Done!', quote=True)
    except PixivError as error:
        message.reply_text(error.reason, quote=True)
    except DanbooruError as error:
        message.reply_text(error.msg, quote=True)
    except MoebooruError as error:
        message.reply_text(error.msg, quote=True)
def pixiv_bookmark(update, context):
    message = update.message
    try:
        # args[0] should contain the queried artwork id
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid artwork id!', quote=True)
            return
        pixiv.bookmark(id)
        message.reply_text('Done!', quote=True)
    except (IndexError, ValueError):
        message.reply_text('Usage: /bookmark <artwork_id>', quote=True)
    except PixivError as error:
        message.reply_text(error.reason)
def clear_downloads(update, context):
    message = update.message
    try:
        shutil.rmtree('./downloads')
        message.reply_text("downloads directory cleared successfully.", quote=True)
    except PermissionError:
        message.reply_text("Permission denied.", quote=True) 
    except OSError as error:
        message.reply_text(error.strerror, quote=True)

def error(update, context):
    logger.error('Update "%s" caused error "%s"', update, context.error)
    traceback.print_exc()

def main():
    urlFilter = Filters.entity('url') | Filters.entity('text_link') | Filters.caption_entity('url') | Filters.caption_entity('text_link')

    # Set up the Updater
    updater = Updater(TOKEN, workers=32, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('ping', ping))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('pixiv', pixiv_view, pass_args=True))
    dp.add_handler(CommandHandler('pixiv_download', pixiv_download, pass_args=True))
    dp.add_handler(CommandHandler('bookmark', pixiv_bookmark, Filters.user(user_id=ADMIN_ID), pass_args=True))
    dp.add_handler(CommandHandler('danbooru', danbooru_view, pass_args=True))
    dp.add_handler(CommandHandler('danbooru_download', danbooru_download, pass_args=True))
    dp.add_handler(CommandHandler('yandere', yandere_view, pass_args=True))
    dp.add_handler(CommandHandler('yandere_download', yandere_download, pass_args=True))
    dp.add_handler(CommandHandler('konachan', konachan_view, pass_args=True))
    dp.add_handler(CommandHandler('konachan_download', konachan_download, pass_args=True))
    dp.add_handler(CommandHandler('clear_downloads', clear_downloads, Filters.user(user_id=ADMIN_ID), pass_args=True))
    dp.add_handler(MessageHandler(urlFilter & (~ Filters.update.channel_posts), gallery_update, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    pixiv.login()
    if ENV == 'production':
        # Webhook mode
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
        updater.bot.setWebhook(WEBHOOK_URL + TOKEN)
        logger.info('Set webhook')
    else:
        # Polling mode
        updater.start_polling()
        print('Started polling')

    updater.idle()

if __name__ == '__main__':
    main()