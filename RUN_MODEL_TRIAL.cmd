@echo off
setlocal
cd /d "%~dp0"
python -m scripts.run_sandbox_trial --trial "%USERPROFILE%\AXDEV_TRIAL"
exit /b %errorlevel%
