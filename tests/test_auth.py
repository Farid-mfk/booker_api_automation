import pytest
import allure


@allure.feature("Auth API Tests")
class TestAuthAPI:

    @staticmethod
    def _verify_common_headers_and_time(response):
        with allure.step("Проверить время ответа"):
            assert response.elapsed.total_seconds() < 2.0
        with allure.step("Проверить заголовок Content-Type"):
            assert "application/json" in response.headers.get("Content-Type", "")

    @pytest.fixture(autouse=True)
    def setup_booking(self, api_client, create_booking_data):
        response = api_client.create_booking(create_booking_data)
        self.booking_id = response.json()["bookingid"]
        yield
        valid_auth = api_client.create_token({"username": "admin", "password": "password123"})
        if "token" in valid_auth.json():
            api_client.delete_booking(self.booking_id, valid_auth.json()["token"])

    @allure.title("Получение токена с валидными данными")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_auth_valid_credentials(self, api_client, auth_credentials):
        response = api_client.create_token(auth_credentials)

        assert response.status_code == 200
        assert "token" in response.json()
        self._verify_common_headers_and_time(response)

    @allure.title("Получение токена с неверным паролем")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_auth_wrong_password(self, api_client, auth_wrong_password):
        response = api_client.create_token(auth_wrong_password)

        assert response.status_code == 200
        assert response.json().get("reason") == "Bad credentials"
        assert "token" not in response.json()

    @allure.title("Получение токена с несуществующим пользователем")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_auth_fake_user(self, api_client, auth_fake_user):
        response = api_client.create_token(auth_fake_user)

        assert response.status_code == 200
        assert response.json().get("reason") == "Bad credentials"
        assert "token" not in response.json()

    @allure.title("Использование токена для защищённого запроса")
    @allure.severity(allure.severity_level.NORMAL)
    def test_use_valid_token_for_secured_request(self, api_client, auth_credentials, create_booking_data):
        token = api_client.create_token(auth_credentials).json()["token"]

        update_payload = create_booking_data.copy()
        update_payload["firstname"] = "Authorized"
        response = api_client.update_booking(self.booking_id, update_payload, token)

        assert response.status_code == 200
        assert response.json()["firstname"] == "Authorized"

    @allure.title("Использование неверного токена")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_use_invalid_token_secured_request(self, api_client, create_booking_data):
        update_payload = create_booking_data.copy()
        invalid_token = "invalid_token_123"

        response = api_client.update_booking(self.booking_id, update_payload, invalid_token)

        assert response.status_code == 403

    @allure.title("Запрос без токена к защищённому эндпоинту")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_secured_request_without_token(self, api_client, create_booking_data):
        update_payload = create_booking_data.copy()

        response = api_client.update_booking(self.booking_id, update_payload, token=None)

        assert response.status_code == 403

    @allure.title("Валидация формата токена")
    @allure.severity(allure.severity_level.MINOR)
    def test_token_format_validation(self, api_client, auth_credentials):
        response = api_client.create_token(auth_credentials)
        token = response.json().get("token")

        assert isinstance(token, str)
        assert len(token) > 0

    @allure.title("Повторное получение токена (идемпотентность)")
    @allure.severity(allure.severity_level.MINOR)
    def test_auth_token_idempotency(self, api_client, auth_credentials):
        response_one = api_client.create_token(auth_credentials)
        response_two = api_client.create_token(auth_credentials)

        token_one = response_one.json().get("token")
        token_two = response_two.json().get("token")

        assert response_one.status_code == 200
        assert response_two.status_code == 200
        assert token_one is not None and token_two is not None
        assert isinstance(token_one, str) and isinstance(token_two, str)
