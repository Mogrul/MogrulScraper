from flask import Blueprint, current_app, flash

api = Blueprint("api", __name__)

@api.route("/api/history")
def history():
    settings = current_app.extensions["settings"]
    download_history = settings.download_history

    if not download_history:
        return  {
            "urls": [],
            "message": "No history available",
            "category": "warning",
        }

    return {
        "urls": settings.download_history,
    }