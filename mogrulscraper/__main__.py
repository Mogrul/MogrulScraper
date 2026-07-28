from mogrulscraper.webui import App
from mogrulscraper.scraper import Scraper
from mogrulscraper.log import load_logger

def main():
    load_logger()

    scraper = Scraper()
    scraper.start()

    app = App(scraper)
    app.run_main()

if __name__ == "__main__":
    main()