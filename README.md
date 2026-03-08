# Simple ParaBank UI + API Test Framework

This project is intentionally small and easy to understand.

## Folder structure

- `src/settings.py`: reads `.env` and returns simple runtime settings.
- `src/parabank_api.py`: small API helper functions (`login`, `get_customer`) with URL fallback.
- `src/pages/login_page.py`: minimal login page object.
- `src/pages/register_page.py`: minimal registration page object.
- `tests/conftest.py`: shared pytest fixtures (`settings`, `page`).
- `tests/ui/test_login_page.py`: UI smoke test.
- `tests/e2e/test_register_validate_ui_api.py`: one end-to-end UI + API test.
- `tests/api/test_xml_parser.py`: tiny parser unit test.

## Flow

1. UI test opens ParaBank page and validates content.
2. E2E test registers a user in UI.
3. After UI registration succeeds, the same user is verified through API (`login` then `get_customer`).

## Environment variables

Use `.env` (copy from `.env.example`):

- `UI_BASE_URL`
- `API_BASE_URLS` (comma-separated)
- `RUN_UI` (`true` or `false`)
- `HEADLESS` (`true` or `false`)
- `SLOW_MO_MS` (for visible slower UI actions, e.g. `400`)
- `TIMEOUT_MS`

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python -m playwright install
```

## Run

```bash
pytest -q
```

## Generate Separate UI and API Reports

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\generate_reports.ps1
```

Generated files:
- `reports/ui/junit.xml`
- `reports/ui/console.txt`
- `reports/api/junit.xml`
- `reports/api/console.txt`

If `pytest-html` is installed in your environment, HTML files are also generated:
- `reports/ui/report.html`
- `reports/api/report.html`

## GitHub Actions CI + PDF Reports

This repo includes:
- Workflow: `.github/workflows/ci.yml`
- Reusable action: `.github/actions/run-pytest-suite/action.yml`
- PDF generator: `scripts/generate_pdf_reports.py`

The CI workflow runs UI and API suites separately, stores JUnit/console reports, and generates PDF summaries:
- `reports/pdf/ui-summary.pdf`
- `reports/pdf/api-summary.pdf`
- `reports/pdf/combined-summary.pdf`

## Generate Allure Reports (Separate UI and API)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\generate_allure_reports.ps1
```

Generated Allure result folders:
- `reports/allure-results/ui`
- `reports/allure-results/api`
- `reports/allure-results/combined`

If Allure CLI is installed, HTML reports are generated at:
- `reports/allure-report/ui`
- `reports/allure-report/api`
- `reports/allure-report/combined`

Notes:
- If `RUN_UI=false`, UI and E2E tests are skipped.
- If ParaBank API is unavailable (for example `522`), only API validation in E2E is skipped.
