import logging
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(filename='info.log', filemode='w',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update, context):
    #Send a message when the command /start is issued.
    update.message.reply_text('Hi!')
def ping(update, context):
    update.message.reply_text('pong!')
def echo(update, context):
    #Echo the user message.
    update.message.reply_text(update.message.text)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    TOKEN = os.environ.get('TOKEN')
    # Port is given by Heroku
    PORT = int(os.environ.get('PORT', '8443'))

    # Set up the Updater
    updater = Updater(TOKEN, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('ping', ping))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Webhook mode
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.setWebhook("https://***REMOVED***.herokuapp.com/" + TOKEN)
    # Polling mode
    # updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()