param([string]$ListenAddress='127.0.0.1',[int]$Port=8791)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:LEARNING_HOST=$ListenAddress
$env:LEARNING_PORT=$Port.ToString()
python server.py
