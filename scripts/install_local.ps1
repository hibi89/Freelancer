# WORKNOVA Desk P85 offline installer candidate (unsigned, user-scope only).
# Run from the EXTRACTED package folder. Never touches customer Data folder.
[CmdletBinding()]
param([switch]$DryRun, [switch]$Uninstall, [switch]$ConfirmRemoveApp)
$ErrorActionPreference = 'Stop'
if (-not $env:LOCALAPPDATA) { throw 'LOCALAPPDATA missing' }
$package = Split-Path -Parent $MyInvocation.MyCommand.Path
$installRoot = Join-Path $env:LOCALAPPDATA 'Programs\WORKNOVA Desk'
$app = Join-Path $installRoot 'app'
$data = Join-Path $env:LOCALAPPDATA 'WORKNOVA Desk\Data'
function Assert-PlainPath([string]$p) {
    if (Test-Path -LiteralPath $p) {
        $item = Get-Item -LiteralPath $p -Force
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Reparse point blocked' }
    }
}
Assert-PlainPath $package
Assert-PlainPath $env:LOCALAPPDATA
Assert-PlainPath $installRoot
Assert-PlainPath $app
if ($Uninstall) {
    if (-not $ConfirmRemoveApp) { throw 'Uninstall requires -Uninstall -ConfirmRemoveApp' }
    if ($DryRun) { Write-Output ('DRY RUN: would remove application only: ' + $app); exit 0 }
    if (Test-Path -LiteralPath $app) { Remove-Item -LiteralPath $app -Recurse -Force }
    Write-Output ('Application removed; customer data and backup folders retained: ' + $data)
    exit 0
}
$manifestPath = Join-Path $package 'FILE_MANIFEST.json'
if (-not (Test-Path -LiteralPath $manifestPath)) { throw 'FILE_MANIFEST.json missing' }
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($manifest.format -ne 'worknova-p85-portable-v2') { throw 'Invalid package manifest format' }
$required = @(
  'worknova_desk/__init__.py','worknova_desk/__main__.py',
  'worknova_desk/core.py','worknova_desk/gui.py',
  'worknova_desk/documents.py','worknova_desk/evidence.py',
  'launch.cmd','README_OFFLINE.txt','install_local.ps1','verify_portable.py'
)
$seen = @{}
foreach ($entry in $manifest.files) {
    $name = [string]$entry.path
    if ($name -notmatch '^(worknova_desk/[a-z_][a-z_0-9]*\.py|launch\.cmd|README_OFFLINE\.txt|install_local\.ps1)$') { throw ('Invalid packaged path: ' + $name) }
    if ($seen.ContainsKey($name)) { throw 'Duplicate manifest path' }
    $seen[$name] = $true
    $origin = Join-Path $package ($name.Replace('/', [IO.Path]::DirectorySeparatorChar))
    Assert-PlainPath $origin
    if (-not (Test-Path -LiteralPath $origin -PathType Leaf)) { throw ('Missing package file: ' + $name) }
    if ((Get-Item -LiteralPath $origin).Length -ne [long]$entry.bytes) { throw ('Size mismatch: ' + $name) }
    $actual = (Get-FileHash -LiteralPath $origin -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne ([string]$entry.sha256).ToLowerInvariant()) { throw ('Checksum mismatch: ' + $name) }
}
if ($manifest.files.Count -ne $required.Count -or $seen.Count -ne $required.Count) {
    throw 'Incomplete package manifest'
}
foreach ($name in $required) {
    if (-not $seen.ContainsKey($name)) { throw ('Missing required entry: ' + $name) }
}
if ($DryRun) { Write-Output 'DRY RUN: package hash audit OK; no program/data changes'; exit 0 }
New-Item -ItemType Directory -Force -Path $installRoot | Out-Null
Assert-PlainPath $installRoot
$stage = Join-Path $installRoot ('.staging-' + [guid]::NewGuid().ToString('N'))
$previous = Join-Path $installRoot ('.previous-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N'))
$oldMoved = $false
$appInstalled = $false
try {
    New-Item -ItemType Directory -Path $stage | Out-Null
    foreach ($entry in $manifest.files) {
        $rel = ([string]$entry.path).Replace('/', [IO.Path]::DirectorySeparatorChar)
        $destination = Join-Path $stage $rel
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
        Copy-Item -LiteralPath (Join-Path $package $rel) -Destination $destination
        $digest = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($digest -ne ([string]$entry.sha256).ToLowerInvariant()) { throw ('Staging checksum mismatch: ' + $rel) }
    }
    if (Test-Path -LiteralPath $app) { Move-Item -LiteralPath $app -Destination $previous; $oldMoved = $true }
    Move-Item -LiteralPath $stage -Destination $app
    $appInstalled = $true
    New-Item -ItemType Directory -Force -Path $data | Out-Null
    Write-Output ('WORKNOVA installed (Python required): ' + $app)
    Write-Output ('Start with: ' + (Join-Path $app 'launch.cmd'))
    Write-Output ('Private data separate and untouched: ' + $data)
    if ($oldMoved) { Write-Output ('Previous app retained for rollback: ' + $previous) }
} catch {
    if ($appInstalled -and (Test-Path -LiteralPath $app)) { Remove-Item -LiteralPath $app -Recurse -Force }
    if ($oldMoved -and (Test-Path -LiteralPath $previous)) { Move-Item -LiteralPath $previous -Destination $app }
    throw
} finally {
    if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
}
