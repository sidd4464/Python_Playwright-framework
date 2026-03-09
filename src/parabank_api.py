import json
import logging
from urllib.parse import quote
import xml.etree.ElementTree as ET

import requests

logger = logging.getLogger(__name__)


class ApiUnavailableError(RuntimeError):
    pass


def _xml_to_dict(element: ET.Element):
    if len(element) == 0:
        return element.text or ""

    result: dict[str, object] = {}
    for child in element:
        value = _xml_to_dict(child)
        if child.tag in result:
            existing = result[child.tag]
            if isinstance(existing, list):
                existing.append(value)
            else:
                result[child.tag] = [existing, value]
        else:
            result[child.tag] = value
    return {element.tag: result}


def _parse_response(response: requests.Response):
    body = response.text.strip()
    content_type = response.headers.get("Content-Type", "").lower()
    logger.info("API response content-type=%s status=%s", content_type or "unknown", response.status_code)

    if "json" in content_type or body.startswith("{") or body.startswith("["):
        return response.json()
    if body.startswith("<"):
        return _xml_to_dict(ET.fromstring(body))
    return {"raw": body}


def request_with_fallback(base_urls: list[str], method: str, path: str, timeout_seconds: int = 20):
    errors = []
    normalized = path if path.startswith("/") else f"/{path}"
    logger.info("API request start method=%s path=%s", method, normalized)

    for base_url in base_urls:
        url = f"{base_url}{normalized}"
        try:
            logger.info("API attempt url=%s", url)
            response = requests.request(method=method, url=url, timeout=timeout_seconds)
            response.raise_for_status()
            payload = _parse_response(response)
            logger.info("API success url=%s payload=%s", url, _payload_preview(payload))
            return payload
        except Exception as exc:
            logger.warning("API failure url=%s reason=%s", url, exc)
            errors.append(f"{url}: {exc}")

    logger.error("API unavailable for path=%s", normalized)
    raise ApiUnavailableError("All API base URLs failed.\n" + "\n".join(errors))


def login(base_urls: list[str], username: str, password: str):
    logger.info("API login validation for username=%s", username)
    return request_with_fallback(base_urls, "GET", f"/login/{quote(username)}/{quote(password)}")


def get_customer(base_urls: list[str], customer_id: int | str):
    logger.info("API customer fetch for customer_id=%s", customer_id)
    return request_with_fallback(base_urls, "GET", f"/customers/{customer_id}")


def _payload_preview(payload: object, max_chars: int = 500) -> str:
    try:
        text = json.dumps(payload, ensure_ascii=True)
    except TypeError:
        text = str(payload)
    if len(text) > max_chars:
        return text[:max_chars] + "...(truncated)"
    return text
