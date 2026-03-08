$ErrorActionPreference = 'Continue'

function Supports-AllurePytest {
    $helpText = pytest --help 2>&1
    return ($helpText | Select-String -- "--alluredir").Length -gt 0
}

function Has-AllureCli {
    try {
        $null = allure --version
        return $true
    }
    catch {
        return $false
    }
}

if (-not (Supports-AllurePytest)) {
    Write-Host "allure-pytest plugin not found. Install dependencies first: pip install -e ."
    exit 1
}

New-Item -ItemType Directory -Force -Path reports\allure-results\ui | Out-Null
New-Item -ItemType Directory -Force -Path reports\allure-results\api | Out-Null
New-Item -ItemType Directory -Force -Path reports\allure-results\combined | Out-Null
New-Item -ItemType Directory -Force -Path reports\allure-report\ui | Out-Null
New-Item -ItemType Directory -Force -Path reports\allure-report\api | Out-Null
New-Item -ItemType Directory -Force -Path reports\allure-report\combined | Out-Null

Write-Host 'Running UI tests for Allure...'
pytest tests/ui -q --alluredir=reports/allure-results/ui 2>&1 | Tee-Object reports/allure-results/ui/console.txt
$uiExit = $LASTEXITCODE

Write-Host 'Running API tests for Allure...'
pytest tests/api -q --alluredir=reports/allure-results/api 2>&1 | Tee-Object reports/allure-results/api/console.txt
$apiExit = $LASTEXITCODE

Write-Host "UI exit code: $uiExit"
Write-Host "API exit code: $apiExit"

Write-Host 'Building combined Allure results (UI + API)...'
Copy-Item reports/allure-results/ui/* reports/allure-results/combined -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item reports/allure-results/api/* reports/allure-results/combined -Recurse -Force -ErrorAction SilentlyContinue

if (Has-AllureCli) {
    Write-Host 'Generating Allure HTML report for UI...'
    allure generate reports/allure-results/ui --clean -o reports/allure-report/ui | Out-Host

    Write-Host 'Generating Allure HTML report for API...'
    allure generate reports/allure-results/api --clean -o reports/allure-report/api | Out-Host

    Write-Host 'Generating combined Allure HTML report...'
    allure generate reports/allure-results/combined --clean -o reports/allure-report/combined | Out-Host
}
else {
    Write-Host 'Allure CLI not found. Install it to generate HTML reports from allure-results.'
}

if ($uiExit -ne 0 -or $apiExit -ne 0) {
    exit 1
}

exit 0
