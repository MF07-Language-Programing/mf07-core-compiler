# Package the corp-lang extension and ensure an SVG icon exists
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$root = Resolve-Path (Join-Path $scriptDir "..")
$iconDir = Join-Path $root "images"
$iconPath = Join-Path $iconDir "icon.png"

if (-not (Test-Path $iconPath)) {
    Write-Host "Icon not found. Creating a tiny placeholder PNG icon..."
    # 1x1 PNG (single-line base64, known-valid)
    $b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
    $bytes = [System.Convert]::FromBase64String($b64)
    New-Item -ItemType Directory -Path $iconDir -Force | Out-Null
    [System.IO.File]::WriteAllBytes($iconPath, $bytes)
    Write-Host "Wrote placeholder PNG icon to $iconPath"
}

Push-Location $root
if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    Write-Host "npx not found. Please install Node.js and npm (npx available)." -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "Packaging extension with vsce (via npx)..."
# Run via cmd and pipe 'y' to accept warnings non-interactively; also pass allow-missing-repository
$cmd = "cmd /c `"echo y ^| npx -y @vscode/vsce package --allow-missing-repository`""
Write-Host "Running: $cmd"
Invoke-Expression $cmd
if ($LASTEXITCODE -ne 0) {
    Write-Host "Packaging failed (vsce returned non-zero)." -ForegroundColor Red
    Pop-Location
    exit $LASTEXITCODE
}

Pop-Location
Write-Host "Packaging finished. Check the corp-lang-vscode folder for the .vsix file." 
