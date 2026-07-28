from mogrulscraper.webui import App
from mogrulscraper.scraper import Scraper
from mogrulscraper.log import load_logger
from mogrulscraper.core import Settings

def main():
    settings = Settings()
    load_logger(settings.debug)

    scraper = Scraper()
    scraper.start()

    app = App(scraper)
    app.run_main()

if __name__ == "__main__":
    main()