import logging
from dataclasses import asdict
import json
import queue
import threading
from enum import Enum

from flask import Blueprint, Response

from models import EventDownload, EventTerminal

clients = []
clients_lock = threading.Lock()

dashboard = Blueprint("dashboard", __name__)

def send_client(event: EventDownload | EventTerminal):
    with clients_lock:
        current_clients = list(clients)

    for client in current_clients:
        event_dict = asdict(event)
        if isinstance(event_dict.get("type"), Enum):
            event_dict["type"] = event_dict["type"].value

        client.put(event_dict)

@dashboard.route("/events")
def events():
    client_queue = queue.Queue()

    with clients_lock:
        clients.append(client_queue)

    def generate():
        try:
            while True:
                message = client_queue.get()

                yield (
                    f"data: {json.dumps(message)}\n\n"
                )

        finally:
            with clients_lock:
                if client_queue in clients:
                    clients.remove(client_queue)

    return Response(
        generate(),
        mimetype = "text/event-stream",
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@dashboard.route("/stop", methods = ["POST"])
def pause():
    from scraper import Scraper

    scraper = Scraper()
    logger = logging.getLogger("Web-Client.Stop")
    logger.info(f"Event received")

    if not scraper.is_playing:
        send_client(EventTerminal("Scraper already stopped."))

    else:
        scraper.stop()
        send_client(EventTerminal("Scraper stopping."))

    return "", 204

@dashboard.route("/start", methods = ["POST"])
def start():
    from scraper import Scraper

    scraper = Scraper()
    logger = logging.getLogger("Web-Client.Start")
    logger.info(f"Event received")

    if scraper.is_playing:
        send_client(EventTerminal("Scraper already started."))

    else:
        scraper.start()
        send_client(EventTerminal("Scraper started."))

    return "", 204