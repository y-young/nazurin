# -*- coding: utf-8 -*-
import shutil
import traceback
from config import *
from utils import *
from sites import SiteManager
from sites.Pixiv import PixivError
from sites.Danbooru import DanbooruError
from sites.Moebooru import MoebooruError
from meganz import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
from telegram.error import BadRequest

sites = SiteManager()
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
        message.reply_text('Error: URL not found', quote=True)
        return
    # Telegram counts entity offset and length in UTF-16 code units
    text = text.encode('utf-16-le')
    urls = list()
    for item in entities:
        if item.type == 'text_link':
            urls.append(item.url)
        elif item.type == 'url':
            offset = item.offset
            length = item.length
            urls.append(text[offset * 2:(offset + length) * 2].decode('utf-16-le'))
    src = match_url(urls)
    if not src:
        message.reply_text('Error: No source matched', quote=True)
        return
    logger.info('Collection update: "%s"', src)
    # Perform action
    if user_id == ADMIN_ID:
        # Forward to gallery & Save to album
        bot.forwardMessage(GALLERY_ID, chat_id, message_id)
        chat_id = ALBUM_ID
        message_id = None # No need to reply to message
        is_admin = True
    else:
        # Reply directly to chat
        is_admin = False
    try:
        if src['type'] == 'pixiv':
            pixiv = sites.api('pixiv')()
            if is_admin:
                pixiv.bookmark(src['id'])
            imgs = pixiv.download(id=src['id'])
        elif src['type'] == 'twitter':
            imgs = sites.api('twitter')().download(src['id'])
        elif src['type'] == 'danbooru':
            imgs = sites.api('danbooru')().download(src['id'])
        elif src['type'] in ['yandere', 'konachan']:
            moebooru = sites.api('moebooru')(src['type'])
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
    sites.register_commands(dp)
    dp.add_handler(CommandHandler('clear_downloads', clear_downloads, Filters.user(user_id=ADMIN_ID), pass_args=True))
    dp.add_handler(MessageHandler(urlFilter & (~ Filters.update.channel_posts), gallery_update, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

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