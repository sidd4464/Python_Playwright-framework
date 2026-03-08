from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect


class RegisterPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self, timeout_ms: int = 45000, retries: int = 2):
        url = f"{self.base_url}/register.htm"
        for attempt in range(retries + 1):
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                return
            except PlaywrightTimeoutError:
                if attempt == retries:
                    raise
                self.page.wait_for_timeout(1000)

    def register(self, user: dict[str, str]):
        self.page.fill("#customer\\.firstName", user["first_name"])
        self.page.fill("#customer\\.lastName", user["last_name"])
        self.page.fill("#customer\\.address\\.street", user["street"])
        self.page.fill("#customer\\.address\\.city", user["city"])
        self.page.fill("#customer\\.address\\.state", user["state"])
        self.page.fill("#customer\\.address\\.zipCode", user["zip_code"])
        self.page.fill("#customer\\.phoneNumber", user["phone"])
        self.page.fill("#customer\\.ssn", user["ssn"])
        self.page.fill("#customer\\.username", user["username"])
        self.page.fill("#customer\\.password", user["password"])
        self.page.fill("#repeatedPassword", user["password"])
        self.page.get_by_role("button", name="Register").click()

    def assert_registration_success(self):
        expect(self.page.get_by_text("Your account was created successfully")).to_be_visible()
