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
Write-Host "Next steps (no admin required):"
Write-Host "1. Fully quit IDEA"
Write-Host "2. Restart IDEA"
Write-Host "3. Ctrl+Alt+S -> Plugins -> enable official Chinese (Simplified) Language Pack"
Write-Host "4. Disable community language pack if installed"
Write-Host "5. Settings -> Language and Region -> Language = Chinese (Simplified)"
Write-Host "6. Fully restart IDEA again"
