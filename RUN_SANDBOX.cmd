@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo Usage: RUN_SANDBOX.cmd --repo PATH --plan PATH --state PATH --offline-bundle PATH --bundle-manifest-sha256 SHA256 --model ollama/NAME --execute --confirm-isolated-run
  echo Windows Sandbox Pro/Enterprise required. No auto-install or host fallback.
  exit /b 2
)
python -m scripts.run_sandbox_queue %*
exit /b %errorlevel%
