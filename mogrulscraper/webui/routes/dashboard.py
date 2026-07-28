from flask import Blueprint, Response, current_app
import json

from mogrulscraper.events import event_manager
from mogrulscraper.scraper import Scraper

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/events")
def events():
    client, history = event_manager.subscribe_with_history()

    def generate():
        try:
            for event in history:
                yield f"data: {json.dumps(event)}\n\n"

            while True:
                event = client.get()
                yield f"data: {json.dumps(event)}\n\n"

        finally:
            event_manager.unsubscribe(client)

    return Response(
        generate(),
        mimetype = "text/event-stream",
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@dashboard.route("/start", methods = ["POST"])
def start():
    scraper = current_app.extensions["scraper"]

    if scraper.start():
        return "", 204

    return "Already running", 409

@dashboard.route("/stop", methods = ["POST"])
def stop():
    scraper = current_app.extensions["scraper"]

    if scraper.stop():
        return "", 204

    return "Already stopped", 409