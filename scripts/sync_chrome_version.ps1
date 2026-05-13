$paths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)
$chrome = $null
foreach ($p in $paths) { if (Test-Path $p) { $chrome = $p; break } }
if (-not $chrome) {
    Write-Host "[!] Chrome not found in standard paths, skipping" -ForegroundColor Yellow
    exit 0
}
$ver = (Get-Item $chrome).VersionInfo.FileVersion
$major = ($ver -split '\.')[0]
$mainPy = Join-Path $PSScriptRoot ".." | Join-Path -ChildPath "src\runners\main.py"
$mainPy = (Resolve-Path $mainPy).Path
$src = Get-Content $mainPy -Raw
$new = $src -replace 'version_main=\d+', "version_main=$major"
if ($src -ne $new) {
    Set-Content -Path $mainPy -Value $new -NoNewline
    Write-Host "[OK] version_main set to $major" -ForegroundColor Green
} else {
    Write-Host "[OK] version_main already $major" -ForegroundColor Green
}
