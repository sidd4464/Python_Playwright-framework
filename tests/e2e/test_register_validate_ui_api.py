from datetime import UTC, datetime

import pytest
from pages.register_page import RegisterPage
from parabank_api import ApiUnavailableError, get_customer, login


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
        "username": f"e2e_{stamp}",
        "password": "Password@123",
    }


def _extract_customer_id(payload):
    if isinstance(payload, dict):
        for key in ("id", "customerId", "customer_id"):
            if key in payload:
                return payload[key]
        for value in payload.values():
            found = _extract_customer_id(value)
            if found:
                return found

    if isinstance(payload, list):
        for item in payload:
            found = _extract_customer_id(item)
            if found:
                return found

    return None


def _extract_value(payload, keys):
    if isinstance(payload, dict):
        for key in keys:
            if key in payload and isinstance(payload[key], str):
                return payload[key]
        for value in payload.values():
            found = _extract_value(value, keys)
            if found:
                return found

    if isinstance(payload, list):
        for item in payload:
            found = _extract_value(item, keys)
            if found:
                return found

    return None


def test_register_via_ui_and_validate_customer_via_api(page, settings):
    user = _build_user()

    register_page = RegisterPage(page, settings.ui_base_url)
    register_page.open(timeout_ms=settings.timeout_ms)
    register_page.register(user)
    register_page.assert_registration_success()

    try:
        login_payload = login(settings.api_base_urls, user["username"], user["password"])
    except ApiUnavailableError as exc:
        pytest.skip(f"Skipping API validation because ParaBank API is unavailable: {exc}")

    customer_id = _extract_customer_id(login_payload)
    assert customer_id, f"Could not extract customer id from payload: {login_payload}"

    customer_payload = get_customer(settings.api_base_urls, customer_id)
    assert _extract_value(customer_payload, ["firstName", "first_name"]) == user["first_name"]
    assert _extract_value(customer_payload, ["lastName", "last_name"]) == user["last_name"]
