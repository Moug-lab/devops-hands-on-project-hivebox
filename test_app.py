"""Unit tests for HiveBox application."""

import pytest
from app import app


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