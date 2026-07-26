from flask import Blueprint, request, request, flash, render_template

from shared import Config

config = Blueprint("config", __name__)

@config.route("/config", methods = ["GET"])
def render_config():
    return render_template(
        "config.html",
        config = Config(),
        domains = ["simpcity.cr"],
    )

@config.route("/config", methods = ["POST"])
def receive_config():
    urls = request.form.get("url", "")
    chunk_size = request.form.get("chunk_size", type = int)
    disabled_domains = request.form.getlist("disabled_domains")
    concurrent = request.form.get("concurrent", type = int)
    timeout = request.form.get("timeout", type = int)

    config_data = Config()
    if isinstance(urls, str):
        if urls: config_data.urls = urls.split("\n")

    if chunk_size:
        config_data.chunk_size = chunk_size

    if disabled_domains:
        config_data.disabled_domains = disabled_domains

    if concurrent:
        config_data.concurrent = concurrent

    if timeout:
        config_data.timeout = timeout

    flash(
        "Configuration saved successfully.",
        "success",
    )

    return render_template(
        "config.html",
        config = config_data,
        domains = ["simpcity.cr"]
    )