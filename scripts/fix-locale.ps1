param(
    [string]$IdeVersion = "IntelliJIdea2025.3"
)

$ErrorActionPreference = "Stop"
$configRoot = Join-Path $env:APPDATA "JetBrains\$IdeVersion"
$disabledFile = Join-Path $configRoot "disabled_plugins.txt"

if (-not (Test-Path $configRoot)) {
    Write-Error "IDE config not found: $configRoot"
    exit 1
}

Write-Host "Config: $configRoot"

if (Test-Path $disabledFile) {
    $lines = Get-Content $disabledFile | Where-Object {
        $_.Trim() -and $_.Trim() -ne "com.intellij.zh"
    }
    Set-Content -Path $disabledFile -Value $lines -Encoding UTF8
    Write-Host "Removed com.intellij.zh from disabled_plugins.txt"
} else {
    Write-Host "disabled_plugins.txt not found, skipped"
}

Write-Host ""
Write-Host "IMPORTANT: Community pack alone does NOT work."
Write-Host "You MUST enable the OFFICIAL JetBrains Chinese pack:"
Write-Host "  Chinese (Simplified) Language Pack / zh language pack"
Write-Host ""
Write-Host "Steps (no admin needed):"
Write-Host "1. Fully quit IDEA (all windows)"
Write-Host "2. Restart IDEA"
Write-Host "3. Ctrl+Alt+S -> Plugins -> Installed"
Write-Host "4. Search 'Chinese' -> ENABLE official JetBrains pack (com.intellij.zh)"
Write-Host "5. Community pack (1.0.x) is optional, official pack is required"
Write-Host "6. Ctrl+Alt+S -> Appearance & Behavior -> System Settings -> Language and Region"
Write-Host "7. Language -> Chinese (Simplified) -> OK"
Write-Host "8. Fully restart IDEA again"
