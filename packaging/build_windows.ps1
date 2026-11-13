# Manual unsigned Windows build. Execute only in a verified checkout using Python 3.11.
# No silent installation, code signing, publishing, network sync or auto-update.
$ErrorActionPreference = 'Stop'
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw 'Python launcher py not found' }
py -3.11 -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Tests failed; build aborted' }
# PyInstaller must be installed manually in a disposable venv by the operator.
py -3.11 -c 'import PyInstaller; print(PyInstaller.__version__)'
if ($LASTEXITCODE -ne 0) { throw 'Missing PyInstaller. Review security/licensing before installation' }
py -3.11 -m PyInstaller --noconfirm --clean --onefile --windowed --name BID_AX --paths . run_bidax.py
if ($LASTEXITCODE -ne 0) { throw 'Packaging failed' }
Write-Host 'UNSIGNED TEST BUILD ONLY. Verify SmartScreen/install/uninstall, malware scan, and customer pilot before release.'
