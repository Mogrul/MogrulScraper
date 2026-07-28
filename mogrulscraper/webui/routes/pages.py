from flask import Blueprint, render_template

pages = Blueprint("pages", __name__)

@pages.route("/")
def index():
    return render_template("index.html")

@pages.route("/config")
def config():
    return render_template("config.html")