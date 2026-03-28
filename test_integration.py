"""Integration tests for HiveBox application.

These tests run against a live running instance of the app.
The app must be running on localhost:5000 before executing.
"""

import requests
import pytest


BASE_URL = "http://localhost:5000"


def test_version_endpoint_live():
    """Test /version returns correct structure against live app."""
    response = requests.get(f"{BASE_URL}/version", timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["version"].startswith("v")


def test_metrics_endpoint_live():
    """Test /metrics returns Prometheus metrics against live app."""
    response = requests.get(f"{BASE_URL}/metrics", timeout=10)
    assert response.status_code == 200
    assert "python_info" in response.text


def test_temperature_endpoint_live():
    """Test /temperature returns valid structure against live app."""
    response = requests.get(f"{BASE_URL}/temperature", timeout=10)
    assert response.status_code in (200, 503)
    if response.status_code == 200:
        data = response.json()
        assert "temperature" in data
        assert "unit" in data
        assert "status" in data
        assert data["status"] in ("Too Cold", "Good", "Too Hot")


def test_home_endpoint_live():
    """Test root endpoint returns 200 against live app."""
    response = requests.get(f"{BASE_URL}/", timeout=10)
    assert response.status_code == 200
    assert response.text == "HiveBox is running!"