@echo off
setlocal DisableDelayedExpansion
rem WORKNOVA Desk portable Python launcher; no admin, network or PayPal operations.
if "%LOCALAPPDATA%"=="" (
  echo LOCALAPPDATA is unavailable. 1>&2
  exit /b 2
)
set "WORKNOVA_DATA=%LOCALAPPDATA%\WORKNOVA Desk\Data"
pushd "%~dp0" || exit /b 2
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -B verify_portable.py --root "."
  if errorlevel 1 ( popd & exit /b 2 )
  if not exist "%WORKNOVA_DATA%" mkdir "%WORKNOVA_DATA%" || exit /b 2
  py -3 -B -m worknova_desk.gui --db "%WORKNOVA_DATA%\desk.sqlite"
) else (
  python -B verify_portable.py --root "."
  if errorlevel 1 ( popd & exit /b 2 )
  if not exist "%WORKNOVA_DATA%" mkdir "%WORKNOVA_DATA%" || exit /b 2
  python -B -m worknova_desk.gui --db "%WORKNOVA_DATA%\desk.sqlite"
)
set "WORKNOVA_EXIT=%ERRORLEVEL%"
popd
exit /b %WORKNOVA_EXIT%
