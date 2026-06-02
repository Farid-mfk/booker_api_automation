import requests
import logging

logger = logging.getLogger(__name__)

class BookerClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}

    def create_token(self, payload: dict) -> requests.Response:
        url = f"{self.base_url}/auth"
        logger.info(f"POST {url} | Payload: {payload}")
        return requests.post(url, json=payload, headers=self.headers)

    def create_booking(self, payload: dict) -> requests.Response:
        url = f"{self.base_url}/booking"
        logger.info(f"POST {url} | Payload: {payload}")
        return requests.post(url, json=payload, headers=self.headers)

    def get_booking(self, booking_id: int) -> requests.Response:
        url = f"{self.base_url}/booking/{booking_id}"
        logger.info(f"GET {url}")
        return requests.get(url)

    def update_booking(self, booking_id: int, payload: dict, token: str) -> requests.Response:
        url = f"{self.base_url}/booking/{booking_id}"
        headers = self.headers.copy()
        headers["Cookie"] = f"token={token}"
        logger.info(f"PUT {url} | Token: {token} | Payload: {payload}")
        return requests.put(url, json=payload, headers=headers)

    def partial_update_booking(self, booking_id: int, payload: dict, token: str) -> requests.Response:
        url = f"{self.base_url}/booking/{booking_id}"
        headers = self.headers.copy()
        headers["Cookie"] = f"token={token}"
        logger.info(f"PATCH {url} | Token: {token} | Payload: {payload}")
        return requests.patch(url, json=payload, headers=headers)

    def delete_booking(self, booking_id: int, token: str) -> requests.Response:
        url = f"{self.base_url}/booking/{booking_id}"
        headers = self.headers.copy()
        headers["Cookie"] = f"token={token}"
        logger.info(f"DELETE {url} | Token: {token}")
        return requests.delete(url, headers=headers)
