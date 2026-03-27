"""HiveBox Flask Application.

This module defines a Flask API that exposes environmental sensor data
from openSenseMap for beekeeping use cases.
"""

import os
from datetime import datetime, timezone, timedelta

import requests
from flask import Flask, jsonify

app = Flask(__name__)

APP_VERSION = "v0.0.1"

SENSEBOX_IDS = os.environ.get(
    "SENSEBOX_IDS",
    "5eba5fbad46fb8001b799786,5c21ff8f919bf8001adf2488,5ade1acf223bd80019a1011c",
).split(",")

OPENSENSEMAP_API = "https://api.opensensemap.org"


def get_temperature(box_id):
    """Fetch the latest temperature reading from a senseBox."""
    url = f"{OPENSENSEMAP_API}/boxes/{box_id}/sensors"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        sensors = response.json()
        for sensor in sensors.get("sensors", []):
            if "temperature" in sensor.get("title", "").lower():
                last_measurement = sensor.get("lastMeasurement")
                if not last_measurement:
                    return None
                measured_at = datetime.fromisoformat(
                    last_measurement["createdAt"].replace("Z", "+00:00")
                )
                age = datetime.now(timezone.utc) - measured_at
                if age > timedelta(hours=1):
                    return None
                return float(last_measurement["value"])
    except (requests.RequestException, KeyError, ValueError):
        return None
    return None


@app.route("/")
def home():
    """Return basic status message."""
    return "HiveBox is running!"


@app.route("/version")
def version():
    """Return application version."""
    return jsonify({"version": APP_VERSION})


@app.route("/temperature")
def temperature():
    """Return average temperature from all configured senseBoxes.

    Only includes readings no older than 1 hour.
    Returns 503 if no valid data is available.
    """
    readings = []
    for box_id in SENSEBOX_IDS:
        temp = get_temperature(box_id.strip())
        if temp is not None:
            readings.append(temp)

    if not readings:
        return jsonify({"error": "No valid temperature data available"}), 503

    average = sum(readings) / len(readings)
    return jsonify({"temperature": round(average, 2), "unit": "celsius"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    