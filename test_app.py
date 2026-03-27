"""Unit tests for HiveBox application."""

from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

import pytest
from app import app, get_temperature


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_home_endpoint(client):
    """Test root endpoint works."""
    response = client.get("/")
    assert response.status_code == 200


def test_version_endpoint(client):
    """Test /version endpoint returns version."""
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.get_json()


def test_version_format(client):
    """Test version format follows semantic versioning."""
    response = client.get("/version")
    version = response.get_json()["version"]
    assert version.startswith("v")
    assert len(version[1:].split(".")) == 3


def test_invalid_route(client):
    """Test invalid route returns 404."""
    response = client.get("/invalid")
    assert response.status_code == 404


def test_temperature_endpoint_success(client):
    """Test /temperature returns average when valid data exists."""
    with patch("app.get_temperature") as mock_temp:
        mock_temp.return_value = 22.5
        response = client.get("/temperature")
        assert response.status_code == 200
        data = response.get_json()
        assert "temperature" in data
        assert "unit" in data
        assert data["unit"] == "celsius"


def test_temperature_endpoint_no_data(client):
    """Test /temperature returns 503 when no valid data available."""
    with patch("app.get_temperature") as mock_temp:
        mock_temp.return_value = None
        response = client.get("/temperature")
        assert response.status_code == 503


def test_get_temperature_fresh_data():
    """Test get_temperature returns value for fresh sensor data."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "sensors": [{
            "title": "Temperature",
            "lastMeasurement": {
                "value": "18.5",
                "createdAt": datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S.000Z"
                ),
            },
        }]
    }
    mock_response.raise_for_status = MagicMock()
    with patch("requests.get", return_value=mock_response):
        result = get_temperature("5eba5fbad46fb8001b799786")
        assert result == 18.5


def test_get_temperature_stale_data():
    """Test get_temperature rejects data older than 1 hour."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "sensors": [{
            "title": "Temperature",
            "lastMeasurement": {
                "value": "18.5",
                "createdAt": "2020-01-01T00:00:00.000Z",
            },
        }]
    }
    mock_response.raise_for_status = MagicMock()
    with patch("requests.get", return_value=mock_response):
        result = get_temperature("5eba5fbad46fb8001b799786")
        assert result is None
        