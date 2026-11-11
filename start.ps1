param([int]$Port = 8000)
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (!(Test-Path -LiteralPath $pythonPath)) {
    throw 'Run setup.ps1 first to create the Python environment.'
}
Write-Host "OrthoTrace: http://localhost:$Port (Ctrl+C to stop)"
& $pythonPath -m uvicorn app:app --app-dir (Join-Path $projectRoot 'ML3\site\api') --host 127.0.0.1 --port $Port
exit $LASTEXITCODE
