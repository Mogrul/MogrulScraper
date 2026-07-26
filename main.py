import time

from scraper import Scraper
from shared import Config, load_logger
from web import Web

if __name__ == "__main__":
    config = Config()
    load_logger(config.debug)

    scraper = Scraper()
    scraper.start()

    if config.web_client:
        web = Web()
        web.start()
        try:
            web._thread.join()

        except KeyboardInterrupt:
            pass

    else:
        try:
            scraper._thread.join()

        except KeyboardInterrupt:
            pass