import logging
from dataclasses import asdict
import json
import queue
import threading
from enum import Enum

from flask import Blueprint, Response

from models import EventDownload, EventTerminal
from shared import Config

clients = []
clients_lock = threading.Lock()

terminal_events: list[dict] = []
terminal_events_lock = threading.Lock()

dashboard = Blueprint("dashboard", __name__)

def event_to_dict(event: EventDownload | EventTerminal) -> dict:
    event_dict = asdict(event)

    if isinstance(event_dict.get("type"), Enum):
        event_dict["type"] = event_dict["type"].value

    return event_dict

def send_client(event: EventDownload | EventTerminal):
    event_dict = event_to_dict(event)

    if event.type == "terminal":
        with terminal_events_lock:
            terminal_events.append(event_dict)

    with clients_lock:
        current_clients = list(clients)

    for client in current_clients:
        client.put(event_dict)

def send_terminal(message: str):
    config = Config()

    if config.web_client:
        event = EventTerminal(message)
        send_client(event)

def handle_initial() -> list[dict]:
    from session import Session
    initial_events = []

    # Existing downloads
    session = Session()

    for download in session.get_download_events():
        initial_events.append(event_to_dict(download))

    # Previous terminal events
    with terminal_events_lock:
        initial_events.extend(terminal_events)

    return initial_events

@dashboard.route("/events")
def events():
    client_queue = queue.Queue()

    with clients_lock:
        clients.append(client_queue)

    # Send initial data
    for event in handle_initial():
        client_queue.put(event)

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
        send_client(EventTerminal("Scraper started."))
        try:
            scraper.start()
        except Exception as e:
            logger.error(e)

    return "", 204