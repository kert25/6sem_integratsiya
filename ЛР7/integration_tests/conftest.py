"""Pytest fixtures for API-to-PostgreSQL integration tests."""

import time

import psycopg2
import pytest
import requests

API_URL = "http://127.0.0.1:13000"
DB_SETTINGS = {
    "host": "127.0.0.1",
    "port": 5433,
    "dbname": "db123",
    "user": "user123",
    "password": "password123",
}


@pytest.fixture(scope="session")
def api_session():
    """Return a session after the containerized API and its schema are ready."""
    session = requests.Session()
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            response = session.get(f"{API_URL}/setup", timeout=2)
            if response.status_code in (200, 500):
                return session
        except requests.RequestException:
            time.sleep(1)
    pytest.fail("Containerized API did not become ready within 30 seconds")


@pytest.fixture(scope="session")
def db_connection():
    connection = psycopg2.connect(**DB_SETTINGS)
    yield connection
    connection.close()


@pytest.fixture(autouse=True)
def clean_schools(db_connection, api_session):
    """Keep each scenario independent while preserving the schema."""
    with db_connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE schools RESTART IDENTITY")
    db_connection.commit()
    yield


@pytest.fixture
def create_school(api_session):
    def _create(name: str, location: str):
        return api_session.post(
            API_URL,
            json={"name": name, "location": location},
            timeout=5,
        )

    return _create
