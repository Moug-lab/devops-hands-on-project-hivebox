"""HiveBox Flask Application.

This module defines a simple API with health and version endpoints.
"""

from flask import Flask

app = Flask(__name__)

APP_VERSION = "v1.0.0"


@app.route("/")
def home():
    """Return basic status message."""
    return "HiveBox is running!"


@app.route("/version")
def version():
    """Return application version."""
    return {"version": APP_VERSION}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    