$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$libraryPython = Join-Path $PSScriptRoot '..\.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $libraryPython)) {
    Write-Error 'The Python environment is missing. See DESIGN-README.md for setup instructions.'
    exit 1
}
& $libraryPython manage.py migrate
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host 'The Reading Room: http://127.0.0.1:8000/' -ForegroundColor Green
Write-Host 'Press Ctrl+C to stop the local library.'
& $libraryPython manage.py runserver 127.0.0.1:8000
