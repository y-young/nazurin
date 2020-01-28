import logging
import os
import traceback
from utils import *
from pixiv import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InputMediaPhoto

papi = Pixiv()
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
@typing
def echo(update, context):
    #Echo the user message.
    update.message.reply_text(update.message.text)
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
        imgs = papi.artworkDetail(id)
        media = list()
        for img in imgs:
            media.append(InputMediaPhoto(img['url']))
        bot.send_media_group(chat_id, media, reply_to_message_id=message_id)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /pixiv <artwork_id>')
def error(update, context):
    logger.error('Update "%s" caused error "%s"', update, context.error)
    traceback.print_exc()


def main():
    global api
    ENV = os.environ.get('ENV')
    TOKEN = os.environ.get('TOKEN')
    # Port is given by Heroku
    PORT = int(os.environ.get('PORT', '8443'))
    ADMIN_ID = int(os.environ.get('ADMIN_ID'))
    PIXIV_USER = os.environ.get('PIXIV_USER')
    PIXIV_PASS = os.environ.get('PIXIV_PASS')

    # Set up the Updater
    updater = Updater(TOKEN, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('ping', ping))
    dp.add_handler(CommandHandler('pixiv', pixiv, Filters.user(user_id=ADMIN_ID), pass_args=True))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

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
    updater.idle()

if __name__ == '__main__':
    main()