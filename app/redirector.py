import os
from flask import Flask, request, redirect, abort
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DB_KEY"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Redirection(db.Model):
    __tablename__ = "redirection"
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_url = db.Column(db.String(1024), nullable=False)
    # make destination primary key?
    alias_url = db.Column(db.String(1024), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    ip = db.Column(db.String(20), nullable=False)
    browser = db.Column(db.String(100))
    platform = db.Column(db.String(30))

    def __init__(self, source_url, alias_url):
        self.source_url = source_url
        self.alias_url = alias_url
        self.time = datetime.utcnow()
        self.ip = request.headers.getlist("X-Forwarded-For")[0]
        self.browser = request.user_agent.browser
        self.platform = request.user_agent.platform


def checkAliasExists(alias_url):
    if db.session.query(Redirection).filter(Redirection.alias_url == alias_url).count() > 0:
        return True
    return False


def getSourceURL(alias_url):
    result = db.session.query(Redirection).filter(Redirection.alias_url == alias_url).first()
    if result is not None:
        source = result.source_url
        return source
    else:
        abort(404)


def addLoggingEntry(site):
    data = Logging(site)
    db.session.add(data)
    db.session.commit()


def addRedirectEntry(source_url, alias_url):
    data = Redirection(source_url, alias_url)
    db.session.add(data)
    db.session.commit()


@app.route("/", methods=["GET"])
def home():
    source = "https://github.com/aditeyabaral/redirector"
    return redirect(source, 302)


@app.route("/register", methods=["POST"])
def registerLink():
    source_url = request.form.get("source_url", default=None)
    alias_url = request.form.get("alias_url", default=None)

    if source_url is None or alias_url is None:
        status_message = f"Source or Destination cannot be empty", 400

    else:
        if not checkAliasExists(alias_url):
            addRedirectEntry(source_url, alias_url)
            status_message = f"{alias_url} is now successfully linked to {source_url}", 200

        else:
            status_message = f"{alias_url} already exists", 400

    return status_message


@app.route("/<destination>", methods=["GET"])
def redirectLink(alias_url):
    source = getSourceURL(alias_url)
    return redirect(source, 302)


if __name__ == "__main__":
    app.run()