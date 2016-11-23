#!/usr/bin/env python2

import settings
import handlers
import logging
from telegram.ext import Updater, InlineQueryHandler, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    updater = Updater(settings.TELEGRAM_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('help', handlers.help))
    updater.dispatcher.add_handler(InlineQueryHandler(handlers.inline))

    updater.start_polling()
    updater.idle()
