from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect


class LoginPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self, timeout_ms: int = 45000, retries: int = 2):
        url = f"{self.base_url}/index.htm"
        for attempt in range(retries + 1):
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                return
            except PlaywrightTimeoutError:
                if attempt == retries:
                    raise
                self.page.wait_for_timeout(1000)

    def assert_loaded(self):
        expect(self.page.get_by_role("heading", name="Customer Login")).to_be_visible()

    def login(self, username: str, password: str):
        self.page.fill("input[name='username']", username)
        self.page.fill("input[name='password']", password)
        self.page.get_by_role("button", name="Log In").click()

    def assert_login_success(self):
        expect(self.page.get_by_role("heading", name="Accounts Overview")).to_be_visible()
