"""HiveBox Application with Metrics and Temperature Service."""

import os
import requests
from flask import Flask, jsonify
from prometheus_client import generate_latest, Counter

app = Flask(__name__)

APP_VERSION = "v1.1.0"

REQUEST_COUNT = Counter("app_requests_total", "Total API Requests")

# ENV CONFIG
SENSEBOX_IDS = os.getenv(
    "SENSEBOX_IDS",
    "5eba5fbad46fb8001b799786,5c21ff8f919bf8001adf2488"
).split(",")


@app.route("/")
def home():
    REQUEST_COUNT.inc()
    return "HiveBox running"


@app.route("/version")
def version():
    REQUEST_COUNT.inc()
    return {"version": APP_VERSION}


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": "text/plain"}


@app.route("/temperature")
def temperature():
    REQUEST_COUNT.inc()

    temps = []

    for box in SENSEBOX_IDS:
        url = f"https://api.opensensemap.org/boxes/{box}"
        res = requests.get(url, timeout=5)

        if res.status_code == 200:
            data = res.json()
            for sensor in data.get("sensors", []):
                if sensor.get("title") == "Temperatur":
                    temps.append(float(sensor["lastMeasurement"]["value"]))

    if not temps:
        return {"error": "No data"}, 503

    avg = sum(temps) / len(temps)

    if avg < 10:
        status = "Too Cold"
    elif 11 <= avg <= 36:
        status = "Good"
    else:
        status = "Too Hot"

    return jsonify({
        "temperature": round(avg, 2),
        "unit": "°C",
        "status": status
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    