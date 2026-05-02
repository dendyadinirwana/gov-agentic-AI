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

if ($env:GOV_AGENTIC_INSTALL_ARGS) {
  $Forwarded = [System.Management.Automation.PSParser]::Tokenize($env:GOV_AGENTIC_INSTALL_ARGS, [ref]$null) | Where-Object { $_.Type -eq 'CommandArgument' -or $_.Type -eq 'CommandParameter' } | ForEach-Object { $_.Content }
  if ($Forwarded.Count -gt 0) {
    & $PSCommandPath @Forwarded
    exit $LASTEXITCODE
  }
}
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
}

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
