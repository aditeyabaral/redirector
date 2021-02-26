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
    source = db.Column(db.String(1024), nullable=False)
    # make destination primary key?
    destination = db.Column(db.String(1024), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    ip = db.Column(db.String(20), nullable=False)
    browser = db.Column(db.String(100))
    platform = db.Column(db.String(30))

    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        self.time = datetime.utcnow()
        self.ip = request.headers.getlist("X-Forwarded-For")[0]
        self.browser = request.user_agent.browser
        self.platform = request.user_agent.platform


class Logging(db.Model):
    __tablename__ = "logging"
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime, nullable=False)
    ip = db.Column(db.String(20), nullable=False)
    browser = db.Column(db.String(100))
    platform = db.Column(db.String(30))
    site = db.Column(db.String(1024), nullable=False)

    def __init__(self, site_name):
        self.site = site_name
        self.time = datetime.utcnow()
        self.ip = request.headers.getlist("X-Forwarded-For")[0]
        self.platform = request.user_agent.platform
        self.browser = request.user_agent.browser


def checkDestinationExists(destination):
    if db.session.query(Redirection).filter(Redirection.destination == destination).count() > 0:
        return True
    return False


def getSource(destination):
    result = db.session.query(Redirection).filter(Redirection.destination == destination).first()
    if result is not None:
        source = result.source
        return source
    else:
        abort(404)


def addLoggingEntry(site_name):
    data = Logging(site_name)
    db.session.add(data)
    db.session.commit()


def addRedirectEntry(source, destination):
    data = Redirection(source, destination)
    db.session.add(data)
    db.session.commit()


@app.route("/", methods=["GET"])
def home():
    source = "https://github.com/aditeyabaral/redirector"
    addLoggingEntry("home")
    return redirect(source, 302)


@app.route("/register", methods=["POST"])
def registerLink():
    source = request.form.get("source", default=None)
    destination = request.form.get("destination", default=None)

    if source is None or destination is None:
        status_message = f"Source or Destination cannot be empty", 400

    else:
        if not checkDestinationExists(destination):
            addRedirectEntry(source, destination)
            status_message = f"{destination} is now successfully linked to {source}", 200

        else:
            status_message = f"{destination} already exists", 400

    addLoggingEntry("register")
    return status_message


@app.route("/<destination>", methods=["GET"])
def redirectLink(destination):
    source = getSource(destination)
    addLoggingEntry(source)
    return redirect(source, 302)


# @app.route("/delete/", methods=["POST"])
# def deleteLink():
#    source = request.form.get("source", default=None)
#    destination = request.form.get("destination", default=None)
#
#    if source is None or destination is None:
#        status_message = f"Source or Destination cannot be empty", 400
#     pass


if __name__ == "__main__":
    app.run()