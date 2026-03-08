from urllib.parse import quote
import xml.etree.ElementTree as ET

import requests


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

    if "json" in content_type or body.startswith("{") or body.startswith("["):
        return response.json()
    if body.startswith("<"):
        return _xml_to_dict(ET.fromstring(body))
    return {"raw": body}


def request_with_fallback(base_urls: list[str], method: str, path: str, timeout_seconds: int = 20):
    errors = []
    normalized = path if path.startswith("/") else f"/{path}"

    for base_url in base_urls:
        url = f"{base_url}{normalized}"
        try:
            response = requests.request(method=method, url=url, timeout=timeout_seconds)
            response.raise_for_status()
            return _parse_response(response)
        except Exception as exc:
            errors.append(f"{url}: {exc}")

    raise ApiUnavailableError("All API base URLs failed.\n" + "\n".join(errors))


def login(base_urls: list[str], username: str, password: str):
    return request_with_fallback(base_urls, "GET", f"/login/{quote(username)}/{quote(password)}")


def get_customer(base_urls: list[str], customer_id: int | str):
    return request_with_fallback(base_urls, "GET", f"/customers/{customer_id}")
