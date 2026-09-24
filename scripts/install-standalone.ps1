param(
    [string]$IdeVersion = "IntelliJIdea2025.3",
    [string]$ZipPath = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

if (-not $ZipPath) {
    $zip = Get-ChildItem (Join-Path $root "releases\idea-chinese-standalone-*.zip") |
        Sort-Object Name -Descending |
        Select-Object -First 1
    if (-not $zip) {
        $zip = Get-ChildItem (Join-Path $root "dist\idea-chinese-standalone-*.zip") |
            Sort-Object Name -Descending |
            Select-Object -First 1
    }
    if (-not $zip) {
        Write-Error "No standalone zip found. Run: python scripts/l10n.py build --version x.y.z"
        exit 1
    }
    $ZipPath = $zip.FullName
}

$configRoot = Join-Path $env:APPDATA "JetBrains\$IdeVersion"
$pluginsRoot = Join-Path $configRoot "plugins"
$disabledFile = Join-Path $configRoot "disabled_plugins.txt"

if (-not (Test-Path $pluginsRoot)) {
    New-Item -ItemType Directory -Force -Path $pluginsRoot | Out-Null
}

$staging = Join-Path $env:TEMP "idea-chinese-install"
if (Test-Path $staging) { Remove-Item $staging -Recurse -Force }
New-Item -ItemType Directory -Force -Path $staging | Out-Null

Expand-Archive -Path $ZipPath -DestinationPath $staging -Force
$bundle = Get-ChildItem $staging -Directory | Select-Object -First 1
if (-not $bundle) {
    Write-Error "Invalid zip layout"
    exit 1
}

$target = Join-Path $pluginsRoot $bundle.Name
if (Test-Path $target) { Remove-Item $target -Recurse -Force }
Move-Item $bundle.FullName $target
Remove-Item $staging -Recurse -Force

$disabled = @()
if (Test-Path $disabledFile) {
    $disabled = Get-Content $disabledFile | ForEach-Object { $_.Trim() } | Where-Object { $_ }
}
$toDisable = @("com.intellij.zh")
foreach ($id in $toDisable) {
    if ($disabled -notcontains $id) { $disabled += $id }
}
$enabled = $disabled | Where-Object { $_ -ne "com.chinese.idea.localization" }
Set-Content -Path $disabledFile -Value $enabled -Encoding UTF8

Write-Host "Installed: $target"
Write-Host "Disabled official pack: com.intellij.zh"
Write-Host ""
Write-Host "Next:"
Write-Host "1. Fully quit IDEA"
Write-Host "2. Restart IDEA"
Write-Host "3. Ctrl+Alt+S -> Appearance & Behavior -> System Settings -> Language and Region"
Write-Host "4. Language -> Chinese (Simplified) standalone / zh-CN"
Write-Host "5. Fully restart IDEA again"
