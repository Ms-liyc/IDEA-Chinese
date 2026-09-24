param(
    [Parameter(Position = 0)]
    [ValidateSet("init", "extract", "import-zh", "sync", "validate", "report", "build")]
    [string]$Command = "report",

    [string]$IdeaPath,
    [string]$Version = "1.0.0",
    [switch]$Force,
    [switch]$Strict,
    [switch]$Output
)

$root = Split-Path -Parent $PSScriptRoot
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "未找到 python，请先安装 Python 3.10+"
    exit 1
}

$argsList = @("scripts/l10n.py", $Command)
if ($IdeaPath) { $argsList += @("--idea-path", $IdeaPath) }
if ($Force) { $argsList += "--force" }
if ($Strict) { $argsList += "--strict" }
if ($Output) { $argsList += "--output" }
if ($Command -eq "build") { $argsList += @("--version", $Version) }

Push-Location $root
try {
    & python @argsList
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
