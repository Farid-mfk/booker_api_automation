import pytest
import logging
import os
from config import BASE_URL
from api_client.booker_client import BookerClient

from data.test_data import AUTH_CREDENTIALS, CREATE_BOOKING_DATA

@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/booker_test.log", mode="w", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

@pytest.fixture(scope="session")
def auth_credentials():
    return AUTH_CREDENTIALS

@pytest.fixture(scope="session")
def create_booking_data():
    return CREATE_BOOKING_DATA

@pytest.fixture(scope="session")
def api_client():
    return BookerClient(base_url=BASE_URL)
