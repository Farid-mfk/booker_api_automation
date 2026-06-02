import allure
from jsonschema import validate
from schemas.schemas import BOOKING_SCHEMA


@allure.feature("Booking Cycle E2E")
class TestBookingE2E:

    def _verify_common_headers_and_time(self, response):
        with allure.step("Проверить время ответа (Шаг 11)"):
            assert response.elapsed.total_seconds() < 2.0

        with allure.step("Проверить заголовок Content-Type (Шаг 12)"):
            assert "application/json" in response.headers.get("Content-Type", "")

    @allure.title("Полный цикл бронирования: авторизация → создание → обновление → удаление")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_booking_e2e_lifecycle(self, api_client, auth_credentials, create_booking_data):
        booking_id = None
        auth_token = None

        # --- ШАГ 1: Авторизация ---
        with allure.step("Шаг 1: Получить токен авторизации"):
            response = api_client.create_token(auth_credentials)
            assert response.status_code == 200
            assert "token" in response.json()

            auth_token = response.json()["token"]
            self._verify_common_headers_and_time(response)

        # --- ШАГ 2 и 3: Создание брони и сохранение ID ---
        with allure.step("Шаг 2-3: Создать новую бронь и сохранить ID"):
            response = api_client.create_booking(create_booking_data)
            assert response.status_code == 200

            res_json = response.json()
            assert "bookingid" in res_json

            booking_id = res_json["bookingid"]
            allure.attach(str(booking_id), name="Сохраненный Booking ID", attachment_type=allure.attachment_type.TEXT)
            self._verify_common_headers_and_time(response)

        # --- ШАГ 4: Получение брони ---
        with allure.step("Шаг 4: Получить созданную бронь по ID"):
            response = api_client.get_booking(booking_id)
            assert response.status_code == 200

            res_json = response.json()
            assert res_json["firstname"] == create_booking_data["firstname"]
            self._verify_common_headers_and_time(response)

        # --- ШАГ 5: Валидация схемы ---
        with allure.step("Шаг 5: Валидировать схему ответа GET"):
            validate(instance=response.json(), schema=BOOKING_SCHEMA)

        # --- ШАГ 6: Полное обновление (PUT) ---
        with allure.step("Шаг 6: Обновить бронь (полное обновление)"):
            update_payload = create_booking_data.copy()
            update_payload["firstname"] = "Updated"
            update_payload["lastname"] = "Updated"

            response = api_client.update_booking(booking_id, update_payload, auth_token)
            assert response.status_code == 200
            assert response.json()["firstname"] == "Updated"
            self._verify_common_headers_and_time(response)

        # --- ШАГ 7: Проверка обновления (GET) ---
        with allure.step("Шаг 7: Проверить обновление через GET"):
            response = api_client.get_booking(booking_id)
            assert response.status_code == 200
            assert response.json()["lastname"] == "Updated"

        # --- ШАГ 8: Частичное обновление (PATCH) ---
        with allure.step("Шаг 8: Частично обновить бронь (PATCH)"):
            patch_payload = {"totalprice": 200}

            response = api_client.partial_update_booking(booking_id, patch_payload, auth_token)
            assert response.status_code == 200

            res_json = response.json()
            assert res_json["totalprice"] == 200
            assert res_json["firstname"] == "Updated"
            self._verify_common_headers_and_time(response)

        # --- ШАГ 9: Удаление брони (DELETE) ---
        with allure.step("Шаг 9: Удалить бронь"):
            response = api_client.delete_booking(booking_id, auth_token)
            assert response.status_code == 201

        # --- ШАГ 10: Проверка удаления ---
        with allure.step("Шаг 10: Проверить удаление (GET на удаленный ID)"):
            response = api_client.get_booking(booking_id)
            assert response.status_code == 404
