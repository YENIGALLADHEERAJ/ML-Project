$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (!(Test-Path -LiteralPath '.venv\Scripts\python.exe')) { py -3.11 -m venv .venv }
if ($LASTEXITCODE) { exit $LASTEXITCODE }
& .\.venv\Scripts\python.exe -m pip install --timeout 180 -r ML3\site\api\requirements.txt
exit $LASTEXITCODE
