from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for

from mogrulscraper.hosts import HOSTS
from mogrulscraper.core import format_bytes

pages = Blueprint("pages", __name__)

@pages.route("/")
def index():
    settings = current_app.extensions["settings"]

    return render_template(
        "index.html",
        downloaded_bytes = format_bytes(settings.stats.downloaded_bytes),
        downloaded_total = settings.stats.downloaded_total,
    )

@pages.route("/settings", methods = ["GET", "POST"])
def config():
    settings = current_app.extensions["settings"]

    if request.method == "POST":
        settings.urls = request.form.get("urls", [])
        settings.excluded_domains = request.form.get("excluded_domains", [])

        settings.chunk_size = int(
            request.form.get("chunk_size") or settings.chunk_size
        )
        settings.concurrent_downloads = int(
            request.form.get("concurrent") or settings.concurrent_downloads
        )
        settings.timeout = int(
            request.form.get("timeout") or settings.timeout
        )
        settings.porndb_token = request.form.get(
            "porndb_token",
            settings.porndb_token
        )

        flash("Settings updated", "success")

    return render_template(
        "settings.html",
        settings = settings,
        hosts = HOSTS.keys(),
    )