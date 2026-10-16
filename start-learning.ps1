param([string]$ListenAddress='127.0.0.1',[int]$Port=8791)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Python 3.11+ is required; no runtime is installed automatically.' }
python scripts/start_local.py --host $ListenAddress --port $Port
if ($LASTEXITCODE -ne 0) { throw 'ThinkLab did not confirm startup. See the error above.' }
