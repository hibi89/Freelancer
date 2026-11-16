@echo off
setlocal
cd /d "%~dp0"
python -m scripts.req_status
exit /b %errorlevel%
