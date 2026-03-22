"""HiveBox application - DevOps End-to-End Hands-On Project.

A REST API that reads environmental sensor data from openSenseMap
to help beekeepers monitor their hive conditions.
"""

from datetime import datetime, timezone, timedelta
import requests
from flask import Flask, jsonify

# App version following Semantic Versioning
APP_VERSION = "v0.0.1"

# openSenseMap senseBox IDs
SENSEBOX_IDS = [
    "5eba5fbad46fb8001b799786",
    "5c21ff8f919bf8001adf2488",
    "5ade1acf223bd80019a1011c",
]

# openSenseMap API base URL
OPENSENSEMAP_API = "https://api.opensensemap.org"

# Maximum age of sensor data in minutes
MAX_DATA_AGE_MINUTES = 60

app = Flask(__name__)


def get_temperature(sensebox_id):
    """Fetch temperature from a single senseBox.

    Args:
        sensebox_id: The openSenseMap senseBox ID string.

    Returns:
        Temperature as float or None if unavailable or too old.
    """
    url = f"{OPENSENSEMAP_API}/boxes/{sensebox_id}"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        return None

    data = response.json()
    sensors = data.get("sensors", [])

    for sensor in sensors:
        if "temperatur" in sensor.get("title", "").lower():
            last_measurement = sensor.get("lastMeasurement")
            if not last_measurement:
                return None

            # Check data is not older than MAX_DATA_AGE_MINUTES
            created_at = last_measurement.get("createdAt", "")
            measurement_time = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            )
            age = datetime.now(timezone.utc) - measurement_time
            if age > timedelta(minutes=MAX_DATA_AGE_MINUTES):
                return None

            return float(last_measurement.get("value", 0))

    return None


@app.route("/version")
def version():
    """Return the current application version.

    Returns:
        JSON response with version string.
    """
    return jsonify({"version": APP_VERSION})


@app.route("/temperature")
def temperature():
    """Return average temperature from all configured senseBoxes.

    Fetches temperature data from openSenseMap API for all
    configured senseBox IDs and returns the average of valid
    readings (data must be no older than 1 hour).

    Returns:
        JSON response with average temperature or error message.
    """
    temperatures = []

    for sensebox_id in SENSEBOX_IDS:
        temp = get_temperature(sensebox_id)
        if temp is not None:
            temperatures.append(temp)

    if not temperatures:
        return jsonify({"error": "No valid temperature data available"}), 503

    avg_temp = round(sum(temperatures) / len(temperatures), 2)
    return jsonify({
        "temperature": avg_temp,
        "unit": "°C",
        "sensors_used": len(temperatures),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
