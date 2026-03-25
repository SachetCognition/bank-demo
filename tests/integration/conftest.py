import pytest
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
AUTH_URL = os.getenv("AUTH_URL", "http://localhost:8000")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:5000")

@pytest.fixture
def base_url():
    return BASE_URL

@pytest.fixture
def auth_url():
    return AUTH_URL

@pytest.fixture
def dashboard_url():
    return DASHBOARD_URL
