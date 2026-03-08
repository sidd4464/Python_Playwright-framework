import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    ui_base_url: str
    api_base_urls: list[str]
    run_ui: bool
    headless: bool
    slow_mo_ms: int
    timeout_ms: int


def _load_env_file(path: str = ".env") -> None:
    env_file = Path(path)
    if not env_file.exists():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        key, value = text.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def load_settings() -> Settings:
    _load_env_file()

    ui_base_url = os.getenv("UI_BASE_URL", "https://parabank.parasoft.com/parabank")
    api_urls_raw = os.getenv(
        "API_BASE_URLS",
        "http://parabank.parasoft.com:8080/parabank/services/bank,https://parabank.parasoft.com/parabank/services/bank",
    )
    api_base_urls = [url.strip().rstrip("/") for url in api_urls_raw.split(",") if url.strip()]

    return Settings(
        ui_base_url=ui_base_url.rstrip("/"),
        api_base_urls=api_base_urls,
        run_ui=_to_bool(os.getenv("RUN_UI"), True),
        headless=_to_bool(os.getenv("HEADLESS"), False),
        slow_mo_ms=_to_int(os.getenv("SLOW_MO_MS"), 300),
        timeout_ms=_to_int(os.getenv("TIMEOUT_MS"), 45000),
    )
