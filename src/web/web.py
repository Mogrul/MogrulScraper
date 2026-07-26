import logging
import os
import secrets
from threading import Thread

from flask import Flask

from scraper import Scraper
from shared import SingletonMeta, Config


class Web(Flask, metaclass = SingletonMeta):
    def __init__(self):
        super().__init__(
            __name__,
            template_folder = os.getcwd() + "\\web\\templates",
            static_folder = os.getcwd() + "\\web\\static"
        )
        self._logger = logging.getLogger("Web-Client")
        self._config = Config()

        self.config["SECRET_KEY"] = secrets.token_urlsafe(16)
        self._thread = Thread(
            target = self._start
        )

    def start(self):
        self._thread.start()

    def _start(self):
        self._register_blueprints()
        self._on_startup()
        self.run(
            host = self._config.host,
            port = self._config.port,
            debug = self._config.debug,
            use_reloader = False,
        )

    def _on_startup(self):
        self.logger.info(
            f"{f'Host:':<20} http://{self._config.host}:{self._config.port}\n"
            f"{f'Templates:':<20} {self.template_folder}\n"
            f"{f'Static:':<20} {self.static_folder}\n"
            f"{f'Blueprints:':<20} {", ".join(self.blueprints.keys())}\n"
        )

    def _register_blueprints(self):
        from .routes import home, config, dashboard

        self.register_blueprint(home)
        self.register_blueprint(config)
        self.register_blueprint(dashboard)