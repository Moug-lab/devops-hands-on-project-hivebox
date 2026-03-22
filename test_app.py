"""Unit tests for HiveBox application.

Tests for the Flask API endpoints and helper functions.
"""

from unittest.mock import patch, MagicMock
import pytest
from app import app, get_temperature, APP_VERSION


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_version_endpoint(client):
    """Test /version endpoint returns correct version."""
    response = client.get("/version")
    assert response.status_code == 200
    assert response.get_json()["version"] == APP_VERSION


def test_version_format(client):
    """Test /version endpoint returns semantic version format."""
    response = client.get("/version")
    version = response.get_json()["version"]
    assert version.startswith("v")
    parts = version[1:].split(".")
    assert len(parts) == 3


def test_temperature_endpoint_success(client):
    """Test /temperature endpoint with mocked API response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "sensors": [
            {
                "title": "Temperatur",
                "lastMeasurement": {
                    "value": "20.5",
                    "createdAt": "2099-01-01T00:00:00.000Z",
                },
            }
        ]
    }

    with patch("app.requests.get", return_value=mock_response):
        response = client.get("/temperature")
        assert response.status_code == 200
        data = response.get_json()
        assert "temperature" in data
        assert "unit" in data
        assert data["unit"] == "°C"


def test_temperature_endpoint_no_data(client):
    """Test /temperature returns 503 when no valid data available."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"sensors": []}

    with patch("app.requests.get", return_value=mock_response):
        response = client.get("/temperature")
        assert response.status_code == 503


def test_get_temperature_api_failure():
    """Test get_temperature returns None on API failure."""
    mock_response = MagicMock()
    mock_response.status_code = 500

    with patch("app.requests.get", return_value=mock_response):
        result = get_temperature("fake-id")
        assert result is None