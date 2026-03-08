$ErrorActionPreference = 'Continue'

New-Item -ItemType Directory -Force -Path reports\ui | Out-Null
New-Item -ItemType Directory -Force -Path reports\api | Out-Null

function Supports-HtmlReport {
    $helpText = pytest --help 2>&1
    return ($helpText | Select-String -- "--html").Length -gt 0
}

$hasHtml = Supports-HtmlReport

Write-Host 'Running UI tests and generating UI report...'
if ($hasHtml) {
    pytest tests/ui -q --html=reports/ui/report.html --self-contained-html --junitxml=reports/ui/junit.xml 2>&1 | Tee-Object reports/ui/console.txt
} else {
    pytest tests/ui -q --junitxml=reports/ui/junit.xml 2>&1 | Tee-Object reports/ui/console.txt
}
$uiExit = $LASTEXITCODE

Write-Host 'Running API tests and generating API report...'
if ($hasHtml) {
    pytest tests/api -q --html=reports/api/report.html --self-contained-html --junitxml=reports/api/junit.xml 2>&1 | Tee-Object reports/api/console.txt
} else {
    pytest tests/api -q --junitxml=reports/api/junit.xml 2>&1 | Tee-Object reports/api/console.txt
}
$apiExit = $LASTEXITCODE

Write-Host "UI exit code: $uiExit"
Write-Host "API exit code: $apiExit"

if (-not $hasHtml) {
    Write-Host "pytest-html plugin not found. Generated JUnit XML + console logs only."
}

if ($uiExit -ne 0 -or $apiExit -ne 0) {
    exit 1
}

exit 0
