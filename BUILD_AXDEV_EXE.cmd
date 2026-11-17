@echo off
setlocal
cd /d "%~dp0"
rem Offline, non-admin, unsigned personal EXE development build.
rem Do not install packages or download model weights automatically.
py -3.11 -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
  echo PyInstaller is not installed in local Python 3.11.
  echo Obtain approval before any external install, then rerun.
  exit /b 2
)
py -3.11 -m PyInstaller --clean --noconfirm --onefile --windowed ^
  --name AXDevFactory --paths . ^
  --collect-submodules axdev --collect-submodules scripts ^
  scripts\axdev_desktop.py
if errorlevel 1 exit /b 1
if not exist "%~dp0dist\AXDevFactory.exe" exit /b 1
echo Built: %~dp0dist\AXDevFactory.exe
echo UNSIGNED PERSONAL PREVIEW. Owner Windows 11 runtime acceptance is separate.
exit /b 0
