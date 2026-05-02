param(
  [string]$RepoUrl = "https://github.com/dendyadinirwana/gov-agentic-AI.git",
  [string]$TargetDir = "gov-agentic-AI",
  [string]$Runtime,
  [string]$Memory,
  [string]$Governance,
  [string]$Clusters,
  [switch]$Defaults,
  [switch]$Update,
  [string]$Output,
  [string]$ActiveDeployment,
  [string]$McpMode,
  [string]$McpUrl,
  [string]$McpAuthType,
  [string]$McpAuthEnvVar
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

$SafeRepoGeneratedFiles = @(
  "configs/runtime.generated.json",
  "configs/runtime-bootstrap.generated.json",
  "configs/active.deployment.yaml"
)

function Can-RetryPullAfterGeneratedCleanup {
  $dirtyGenerated = git diff --name-only -- @SafeRepoGeneratedFiles 2>$null
  if (-not $dirtyGenerated) {
    return $false
  }
  $otherChanges = git diff --name-only -- . ':(exclude)configs/runtime.generated.json' ':(exclude)configs/runtime-bootstrap.generated.json' ':(exclude)configs/active.deployment.yaml' 2>$null
  return [string]::IsNullOrWhiteSpace(($otherChanges | Out-String))
}

function Get-CurrentGitBranch {
  $branch = git symbolic-ref --quiet --short HEAD 2>$null
  if ([string]::IsNullOrWhiteSpace(($branch | Out-String))) {
    return 'main'
  }
  return ($branch | Select-Object -First 1)
}

function FastForward-UpdateExistingClone {
  $branch = Get-CurrentGitBranch
  git fetch origin $branch | Out-Null
  $currentBranch = git symbolic-ref --quiet --short HEAD 2>$null
  if ([string]::IsNullOrWhiteSpace(($currentBranch | Out-String))) {
    git checkout -B $branch "origin/$branch" | Out-Null
  }
  git merge --ff-only "origin/$branch" | Out-Null
}

function Retry-PullAfterGeneratedCleanup {
  Write-Host "Detected only generated runtime config changes. Resetting them and retrying update ..."
  git checkout -- @SafeRepoGeneratedFiles | Out-Null
  FastForward-UpdateExistingClone
}

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
  try {
    FastForward-UpdateExistingClone
  } catch {
    if (Can-RetryPullAfterGeneratedCleanup) {
      try {
        Retry-PullAfterGeneratedCleanup
      } catch {
        Write-Warning "Could not fast-forward update existing clone after generated-file cleanup; continuing with local files."
      }
    } else {
      Write-Warning "Could not fast-forward update existing clone; continuing with local files."
    }
  }
}

$InstallerArgs = @()
if ($Defaults) { $InstallerArgs += "--defaults" }
if ($Update) { $InstallerArgs += "--update" }
if ($Runtime) { $InstallerArgs += @("--runtime", $Runtime) }
if ($Memory) { $InstallerArgs += @("--memory", $Memory) }
if ($Governance) { $InstallerArgs += @("--governance", $Governance) }
if ($Clusters) { $InstallerArgs += @("--clusters", $Clusters) }
if ($Output) { $InstallerArgs += @("--output", $Output) }
if ($ActiveDeployment) { $InstallerArgs += @("--active-deployment", $ActiveDeployment) }
if ($McpMode) { $InstallerArgs += @("--mcp-mode", $McpMode) }
if ($McpUrl) { $InstallerArgs += @("--mcp-url", $McpUrl) }
if ($McpAuthType) { $InstallerArgs += @("--mcp-auth-type", $McpAuthType) }
if ($McpAuthEnvVar) { $InstallerArgs += @("--mcp-auth-env-var", $McpAuthEnvVar) }

Write-Host "Running Gov-Agentic AI installer ..."
$InvokeArgs = @($PythonCmd + @("scripts/install_gov_agentic_ai.py") + $InstallerArgs)
& $InvokeArgs[0] $InvokeArgs[1..($InvokeArgs.Length-1)]

Write-Host ""
Write-Host "Done. Generated config: $(Join-Path (Get-Location) 'configs/runtime.generated.json')"
Write-Host "Bootstrap config: $(Join-Path (Get-Location) 'configs/runtime-bootstrap.generated.json')"
Write-Host "YAML summary: $(Join-Path (Get-Location) 'configs/active.deployment.yaml')"
Write-Host "Doctor command: python scripts/doctor_gov_agentic_ai.py --runtime generic"
