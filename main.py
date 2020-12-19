import json
import logging
import os

from bot.service import Service
from tele2client.wrappers import logger

CONFIG_FILE = 'config.js'


def main():
    with open(CONFIG_FILE) as fin:
        config = json.load(fin)

    logger.create(config['log_file'], logging.INFO)

    service = Service(os.getenv('TELEGRAM_API_TOKEN'))
    service.init()
    service.run()


if __name__ == '__main__':
    main()
