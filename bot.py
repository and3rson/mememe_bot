#!/usr/bin/env python2

import settings
import handlers
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    updater = Updater(settings.TELEGRAM_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', handlers.start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, handlers.message))
    updater.dispatcher.add_handler(CommandHandler('reset', handlers.reset))
    updater.dispatcher.add_handler(CommandHandler('cancel', handlers.reset))

    updater.start_polling()
    updater.idle()
