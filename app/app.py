import os
import pytz
import logging
import datetime
import gh_md_to_html
from dotenv import load_dotenv
from urllib.parse import urlparse
from flask import Flask, request, redirect, abort

from db import RedirectionDatabase

logging.basicConfig(
    level=logging.NOTSET,
    filemode="w",
    filename="app.log",
    format="%(asctime)s - %(levelname)s - %(name)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s",
)

load_dotenv()
app = Flask(__name__)
IST = pytz.timezone("Asia/Kolkata")


def convert_readme_to_html():
    if "README.html" not in os.listdir():
        html = gh_md_to_html.main("README.md").strip()
        with open("README.html", "w") as f:
            f.write(html)


@app.route("/")
def index():
    try:
        if "README.html" not in os.listdir():
            convert_readme_to_html()
        with open("README.html") as f:
            output = f.read()
            return output, 200
    except Exception as e:
        logging.error(f"Error rendering home page: {e}")
        return "Error occurred while retrieving home page", 500


@app.route("/new", methods=["POST"])
@app.route("/register", methods=["POST"])
def register_new_link():
    source_url = request.json.get("source_url", None)
    alias_name = request.json.get("alias_name", None)
    if source_url is None:
        logging.error("Source URL not provided")
        message_and_error_code = "Source URL not provided", 400
    else:
        if alias_name is None:
            logging.warning("Alias name not provided, generating random alias name")
            alias_name = redirection_db.generate_random_alias_name()
        if redirection_db.check_alias_exists(alias_name):
            logging.error(f"Alias name {alias_name} already exists")
            message_and_error_code = "Alias name already exists", 400
        else:
            ip_address = (
                request.headers.getlist("X-Forwarded-For")[0]
                if request.headers.getlist("X-Forwarded-For")
                else request.remote_addr
            )
            browser = request.headers.get("User-Agent", "Unknown")
            platform = request.headers.get("Platform", "Unknown")
            create_time = datetime.datetime.now(IST)
            logging.info(
                f"Adding new redirection URL: {source_url} -> {alias_name} with create_time: {create_time}, ip_address: {ip_address}, browser: {browser}, platform: {platform}"
            )
            redirection_db.add_new_redirection_url(
                source_url, alias_name, create_time, ip_address, browser, platform
            )
            http_prefix = "https" if request.is_secure else "http"
            message_and_error_code = (
                f"New redirection URL {alias_name} successfully linked to {source_url}. You can now visit the link on {http_prefix}://{urlparse(request.base_url).netloc}/{alias_name}.",
                200,
            )
    return message_and_error_code


@app.route("/<alias_name>")
def redirect_to_source_url(alias_name):
    logging.info(f"Redirection request for alias name: {alias_name}")
    source_url = redirection_db.get_source_url_from_alias_name(alias_name)
    if source_url is None:
        logging.error(f"Alias name {alias_name} not found")
        abort(404)
    else:
        logging.info(f"Redirecting to {source_url}")
        return redirect(source_url, 302)


if __name__ == "__main__":
    redirection_db = RedirectionDatabase()
    convert_readme_to_html()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
