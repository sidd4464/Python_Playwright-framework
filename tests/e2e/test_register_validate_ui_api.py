from datetime import UTC, datetime
import logging

import pytest
from pages.register_page import RegisterPage
from parabank_api import ApiUnavailableError, get_customer, login

logger = logging.getLogger(__name__)


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
    logger.info("E2E start: register user in UI and validate with API")
    user = _build_user()
    logger.info("Generated user username=%s", user["username"])

    register_page = RegisterPage(page, settings.ui_base_url)
    logger.info("Opening register page")
    register_page.open(timeout_ms=settings.timeout_ms)
    logger.info("Submitting registration form")
    register_page.register(user)
    register_page.assert_registration_success()
    logger.info("UI registration success confirmed")

    try:
        logger.info("Calling API login for username=%s", user["username"])
        login_payload = login(settings.api_base_urls, user["username"], user["password"])
    except ApiUnavailableError as exc:
        pytest.skip(f"Skipping API validation because ParaBank API is unavailable: {exc}")

    customer_id = _extract_customer_id(login_payload)
    logger.info("Extracted customer_id=%s from login payload", customer_id)
    assert customer_id, f"Could not extract customer id from payload: {login_payload}"

    logger.info("Calling API customer details endpoint customer_id=%s", customer_id)
    customer_payload = get_customer(settings.api_base_urls, customer_id)
    first_name = _extract_value(customer_payload, ["firstName", "first_name"])
    last_name = _extract_value(customer_payload, ["lastName", "last_name"])
    logger.info("API customer payload resolved first_name=%s last_name=%s", first_name, last_name)

    assert first_name == user["first_name"]
    assert last_name == user["last_name"]
    logger.info("E2E API validation completed successfully")
