param(
  [string]$RepoUrl = "https://github.com/dendyadinirwana/gov-agentic-AI.git",
  [string]$TargetDir = "gov-agentic-AI",
  [string]$Runtime,
  [string]$ShimRoot,
  [string]$Config,
  [switch]$SkipRepo,
  [switch]$SkipSkills,
  [switch]$SkipConfig,
  [switch]$SkipAttach
)

$ErrorActionPreference = "Stop"

function Need-Command($Name) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Missing required command: $Name"
  }
}

Need-Command git

$PythonCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
  $PythonCmd = @("py", "-3")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  $PythonCmd = @("python")
} else {
  throw "Missing Python 3. Please install Python 3 and re-run."
}

if ($TargetDir -eq ".") {
  if (-not (Test-Path ".git")) {
    throw "-TargetDir . requires running from an existing Gov-Agentic AI clone."
  }
  Write-Host "Using existing repository at $(Get-Location)"
} elseif (-not (Test-Path (Join-Path $TargetDir ".git"))) {
  Write-Host "Cloning $RepoUrl into $TargetDir ..."
  git clone $RepoUrl $TargetDir
  Set-Location $TargetDir
} else {
  Write-Host "Using existing repository at $TargetDir"
  Set-Location $TargetDir
  Write-Host "Updating existing clone ..."
  try { git pull --ff-only | Out-Null } catch { Write-Warning "Could not fast-forward update existing clone; continuing with local files." }
}

$DoctorArgs = @()
if ($Runtime) { $DoctorArgs += @("--runtime", $Runtime) }
if ($ShimRoot) { $DoctorArgs += @("--shim-root", $ShimRoot) }
if ($Config) { $DoctorArgs += @("--config", $Config) }
if ($SkipRepo) { $DoctorArgs += "--skip-repo" }
if ($SkipSkills) { $DoctorArgs += "--skip-skills" }
if ($SkipConfig) { $DoctorArgs += "--skip-config" }
if ($SkipAttach) { $DoctorArgs += "--skip-attach" }

$InvokeArgs = @($PythonCmd + @("scripts/doctor_gov_agentic_ai.py") + $DoctorArgs)
& $InvokeArgs[0] $InvokeArgs[1..($InvokeArgs.Length - 1)]
