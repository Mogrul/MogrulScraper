from scraper import Scraper
from shared import Config, load_logger
from web import Web

if __name__ == "__main__":
    config = Config()
    load_logger(config.debug)

    if config.web_client:
        web = Web()
        web.start()

    scraper = Scraper()
    scraper.start()