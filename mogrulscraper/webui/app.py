import logging
import threading
from pathlib import Path

from flask import Flask

from mogrulscraper.webui.routes import pages, dashboard, api
from mogrulscraper.scraper import Scraper
from mogrulscraper.core import Settings, get_secret_key

class App(Flask):
    def __init__(
            self,
            scraper: Scraper,
    ):
        base_dir = Path(__file__).parent

        super().__init__(
            __name__,
            static_folder = str(base_dir / "static"),
            template_folder = str(base_dir / "templates"),
        )

        self._thread = None
        self._logger = logging.getLogger("WebApp")
        self._settings = Settings()

        self.extensions["scraper"] = scraper
        self.extensions["settings"] = self._settings
        self.config["SECRET_KEY"] = get_secret_key("flask_secret_key")

        self.register_blueprint(pages)
        self.register_blueprint(dashboard)
        self.register_blueprint(api)

    def run_thread(self):
        if (
            self._thread
            and self._thread.is_alive()
        ):
            return

        self._thread = threading.Thread(
            target = self.run_main,
            daemon = True,
        )
        self._thread.start()

    def run_main(self):
        self._logger.info(
            "Running on http://127.0.0.1:8080/",
        )
        self.run(
            host = "127.0.0.1",
            port = 8080,
            debug = True,
            use_reloader = False,
        )