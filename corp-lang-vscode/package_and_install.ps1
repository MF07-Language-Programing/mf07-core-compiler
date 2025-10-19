# Package and install corp-lang VS Code extension (Windows)
# Requires: vsce (npm) and code CLI available in PATH
# Usage: Open PowerShell, cd to project root, then: .\corp-lang-vscode\package_and_install.ps1

$extDir = Join-Path $PSScriptRoot '' | Resolve-Path
Push-Location "$PSScriptRoot\.."

if (-not (Get-Command vsce -ErrorAction SilentlyContinue)) {
    Write-Host "vsce not found. Install with: npm install -g vsce" -ForegroundColor Yellow
    Pop-Location
    exit 1
}

Write-Host "Packaging extension..."
Push-Location "corp-lang-vscode"
vsce package
$vsix = Get-ChildItem -Filter "*.vsix" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($null -eq $vsix) {
    Write-Host "No .vsix produced." -ForegroundColor Red
    Pop-Location
    Pop-Location
    exit 1
}
Write-Host "Installing $($vsix.Name) to VS Code..."
code --install-extension $vsix.FullName
Write-Host "Installed. Restart VS Code if needed."
Pop-Location
Pop-Location
