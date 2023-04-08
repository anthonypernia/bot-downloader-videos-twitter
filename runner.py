"""Main runner for the application."""
import logging
import time

import bot.util.constants as c
from bot.config.config import Config
from bot.main_process import MainProcess

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    config = Config(c.CONFIG_FILE)
    print(config.get(c.PATH_TO_DOWNLOAD))
    process = MainProcess(
        config.get(c.PATH_TO_DOWNLOAD), **config.get(c.AUTHENTICATION)  # type: ignore
    )
    while True:
        process.run()
        time.sleep(10)
