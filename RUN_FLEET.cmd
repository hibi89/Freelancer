@echo off
setlocal
cd /d "%~dp0"
python -m scripts.fleet run --execute --confirm-reviewed --max-projects 10 --max-tasks 100
exit /b %errorlevel%
