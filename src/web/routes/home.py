from flask import Blueprint, render_template

home = Blueprint("home", __name__)

@home.route("/", methods = ["GET"])
def index():
    from scraper import Scraper
    scraper = Scraper()

    return render_template(
        "index.html",
        is_playing = scraper.is_playing,
    )