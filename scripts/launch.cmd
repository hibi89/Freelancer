@echo off
setlocal DisableDelayedExpansion
rem WORKNOVA Desk portable Python launcher; no admin, network or PayPal operations.
if "%LOCALAPPDATA%"=="" (
  echo LOCALAPPDATA is unavailable. 1>&2
  exit /b 2
)
set "WORKNOVA_DATA=%LOCALAPPDATA%\WORKNOVA Desk\Data"
if not exist "%WORKNOVA_DATA%" mkdir "%WORKNOVA_DATA%" || exit /b 2
pushd "%~dp0" || exit /b 2
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -m worknova_desk.gui --db "%WORKNOVA_DATA%\desk.sqlite"
) else (
  python -m worknova_desk.gui --db "%WORKNOVA_DATA%\desk.sqlite"
)
set "WORKNOVA_EXIT=%ERRORLEVEL%"
popd
exit /b %WORKNOVA_EXIT%
