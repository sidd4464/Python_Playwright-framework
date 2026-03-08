from datetime import UTC, datetime

import pytest
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from parabank_api import ApiUnavailableError, login


def _build_user():
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return {
        "first_name": "Auto",
        "last_name": f"User{stamp[-4:]}",
        "street": "101 Test Street",
        "city": "Testville",
        "state": "CA",
        "zip_code": "90001",
        "phone": "5551234567",
        "ssn": stamp[-9:],
        "username": f"login_{stamp}",
        "password": "Password@123",
    }


def _extract_customer_id(payload):
    if isinstance(payload, dict):
        for key in ("id", "customerId", "customer_id"):
            if key in payload:
                return payload[key]
        for value in payload.values():
            candidate = _extract_customer_id(value)
            if candidate:
                return candidate

    if isinstance(payload, list):
        for item in payload:
            candidate = _extract_customer_id(item)
            if candidate:
                return candidate

    return None


def test_login_via_ui_and_validate_with_api(page, settings):
    user = _build_user()

    register_page = RegisterPage(page, settings.ui_base_url)
    register_page.open(timeout_ms=settings.timeout_ms)
    register_page.register(user)
    register_page.assert_registration_success()

    page.get_by_role("link", name="Log Out").click()

    login_page = LoginPage(page, settings.ui_base_url)
    login_page.open(timeout_ms=settings.timeout_ms)
    login_page.login(user["username"], user["password"])
    login_page.assert_login_success()

    try:
        login_payload = login(settings.api_base_urls, user["username"], user["password"])
    except ApiUnavailableError as exc:
        pytest.skip(f"Skipping API login validation because ParaBank API is unavailable: {exc}")

    customer_id = _extract_customer_id(login_payload)
    assert customer_id, f"Could not extract customer id from login payload: {login_payload}"
