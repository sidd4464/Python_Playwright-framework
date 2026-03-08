import pytest
from playwright.sync_api import sync_playwright

from settings import Settings, load_settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    return load_settings()


@pytest.fixture
def page(settings: Settings):
    if not settings.run_ui:
        pytest.skip("Skipping UI tests. Set RUN_UI=true to enable browser-based tests.")

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=settings.headless,
                slow_mo=settings.slow_mo_ms,
            )
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(settings.timeout_ms)
            try:
                yield page
            finally:
                context.close()
                browser.close()
    except PermissionError as exc:
        pytest.skip(f"Skipping UI tests because browser process launch is blocked: {exc}")
    except OSError as exc:
        pytest.skip(f"Skipping UI tests because Playwright cannot start: {exc}")
