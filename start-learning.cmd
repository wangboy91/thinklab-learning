@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3.11+ is required. Install it yourself and retry.
  pause
  exit /b 1
)
python scripts\start_local.py %*
if errorlevel 1 (
  echo ThinkLab did not confirm startup. See the error above.
  pause
  exit /b 1
)
