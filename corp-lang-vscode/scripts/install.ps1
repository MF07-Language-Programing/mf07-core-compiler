# Installs the latest produced .vsix for corp-lang into VS Code
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$root = Resolve-Path (Join-Path $scriptDir "..")
$vsix = Get-ChildItem -Path $root -Filter "*.vsix" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($null -eq $vsix) {
    Write-Host "No .vsix found in $root. Run scripts\package.ps1 first." -ForegroundColor Yellow
    exit 1
}

if (-not (Get-Command code -ErrorAction SilentlyContinue)) {
    Write-Host "VS Code 'code' CLI not found in PATH. Install or add it to PATH." -ForegroundColor Red
    exit 1
}

Write-Host "Installing $($vsix.FullName) to VS Code..."
code --install-extension $vsix.FullName
Write-Host "If the extension does not appear, restart VS Code."