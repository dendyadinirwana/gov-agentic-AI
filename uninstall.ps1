param(
  [string]$TargetDir = $(if ($env:TARGET_DIR) { $env:TARGET_DIR } else { 'gov-agentic-AI' }),
  [string]$RepoUrl = $(if ($env:GOV_AGENTIC_REPO_URL) { $env:GOV_AGENTIC_REPO_URL } else { 'https://github.com/dendyadinirwana/gov-agentic-AI.git' })
)

$UninstallArgs = $env:GOV_AGENTIC_UNINSTALL_ARGS

if (-not (Test-Path (Join-Path $TargetDir '.git'))) {
  Write-Host "Cloning $RepoUrl into $TargetDir ..."
  git clone $RepoUrl $TargetDir | Out-Host
} else {
  Write-Host "Using existing repository at $TargetDir"
}

Set-Location $TargetDir
Write-Host 'Running Gov-Agentic AI uninstall ...'
if ([string]::IsNullOrWhiteSpace($UninstallArgs)) {
  python scripts/uninstall_gov_agentic_ai.py
} else {
  Invoke-Expression "python scripts/uninstall_gov_agentic_ai.py $UninstallArgs"
}
