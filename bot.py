# -*- coding: utf-8 -*-
import shutil
import traceback
import config
from utils import typing, logger, sendDocuments, NazurinError
from sites import SiteManager
from storage import Storage
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Defaults, run_async

sites = SiteManager()
storage = Storage()

@run_async
def start(update, context):
    update.message.reply_text('Hi!')
@run_async
@typing
def ping(update, context):
    update.message.reply_text('pong!')
@run_async
@typing
def get_help(update, context):
    update.message.reply_text('''
    小さな小さな賢将, can help you collect images from various sites.
    Commands:
    /ping - pong
    /pixiv <id> - view pixiv artwork
    /pixiv_download <id> - download pixiv artwork
    /danbooru <id> - view danbooru post
    /danbooru_download <id> - download danbooru post
    /yandere <id> - view yandere post
    /yandere_download <id> - download yandere post
    /konachan <id> - view konachan post
    /konachan_download <id> - download konachan post
    /bookmark <id> - bookmark pixiv artwork
    /clear_downloads - clear download cache
    /help - get this help text
    PS: Send Pixiv/Danbooru/Yandere/Konachan/Twitter URL to download image(s)
    ''')
@run_async
def collection_update(update, context):
    message = update.message
    message_id = message.message_id
    chat_id = message.chat_id
    bot = context.bot

    # Match URL
    if message.entities:
        entities = message.entities
        text = message.text
    elif message.caption_entities:
        entities = message.caption_entities
        text = message.caption
    else:
        message.reply_text('Error: URL not found')
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

    result = sites.match(urls)
    if not result:
        message.reply_text('Error: No source matched')
        return
    logger.info('Collection update: site=%s, match=%s', result['site'], result['match'].groups())
    # Forward to gallery & Save to album
    bot.forwardMessage(config.GALLERY_ID, chat_id, message_id)
    chat_id = config.ALBUM_ID
    message_id = None # No need to reply to message

    try:
        imgs = sites.handle_update(result)
        sendDocuments(update, context, imgs, chat_id=chat_id)
        storage.store(imgs)
        message.reply_text('Done!')
    except NazurinError as error:
        message.reply_text(error.msg)
def clear_downloads(update, context):
    message = update.message
    try:
        shutil.rmtree('./downloads')
        message.reply_text("downloads directory cleared successfully.")
    except PermissionError:
        message.reply_text("Permission denied.")
    except OSError as error:
        message.reply_text(error.strerror)

def handle_error(update, context):
    logger.error('Update "%s" caused error "%s"', update, context.error)
    traceback.print_exc()

def main():
    global sites, storage
    defaults = Defaults(quote=True)
    urlFilter = Filters.entity('url') | Filters.entity('text_link') | Filters.caption_entity('url') | Filters.caption_entity('text_link')
    adminFilter = Filters.user(user_id=config.ADMIN_ID)
    sites.load()

    # Set up the Updater
    updater = Updater(config.TOKEN, workers=32, use_context=True, defaults=defaults)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start, adminFilter))
    dp.add_handler(CommandHandler('ping', ping, adminFilter))
    dp.add_handler(CommandHandler('help', get_help, adminFilter))
    sites.register_commands(dp)
    dp.add_handler(CommandHandler('clear_downloads', clear_downloads, adminFilter, pass_args=True))
    dp.add_handler(MessageHandler(adminFilter & urlFilter & (~ Filters.update.channel_posts), collection_update, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(handle_error)

    if config.ENV == 'production':
        # Webhook mode
        updater.start_webhook(listen="0.0.0.0", port=config.PORT, url_path=config.TOKEN)
        updater.bot.setWebhook(url=config.WEBHOOK_URL + config.TOKEN, allowed_updates=["message"])
        logger.info('Set webhook')
    else:
        # Polling mode
        updater.start_polling()
        logger.info('Started polling')

    storage.load()
    updater.idle()

if __name__ == '__main__':
    main()