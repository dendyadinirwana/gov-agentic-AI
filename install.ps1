param(
  [string]$RepoUrl = "https://github.com/dendyadinirwana/gov-agentic-AI.git",
  [string]$TargetDir = "gov-agentic-AI",
  [string]$Runtime,
  [string]$Memory,
  [string]$Governance,
  [string]$Clusters,
  [switch]$Defaults,
  [string]$Output,
  [string]$ActiveDeployment
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

if (-not (Test-Path (Join-Path $TargetDir ".git"))) {
  Write-Host "Cloning $RepoUrl into $TargetDir ..."
  git clone $RepoUrl $TargetDir
} else {
  Write-Host "Using existing repository at $TargetDir"
}

Set-Location $TargetDir

$InstallerArgs = @()
if ($Defaults) { $InstallerArgs += "--defaults" }
if ($Runtime) { $InstallerArgs += @("--runtime", $Runtime) }
if ($Memory) { $InstallerArgs += @("--memory", $Memory) }
if ($Governance) { $InstallerArgs += @("--governance", $Governance) }
if ($Clusters) { $InstallerArgs += @("--clusters", $Clusters) }
if ($Output) { $InstallerArgs += @("--output", $Output) }
if ($ActiveDeployment) { $InstallerArgs += @("--active-deployment", $ActiveDeployment) }

Write-Host "Running Gov-Agentic AI installer ..."
& $PythonCmd[0] $PythonCmd[1..($PythonCmd.Length-1)] scripts/install_gov_agentic_ai.py @InstallerArgs

Write-Host ""
Write-Host "Done. Generated config: $(Join-Path (Get-Location) 'configs/runtime.generated.json')"
Write-Host "YAML summary: $(Join-Path (Get-Location) 'configs/active.deployment.yaml')"
