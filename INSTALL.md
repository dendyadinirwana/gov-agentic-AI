# Install Gov-Agentic AI from Terminal

This repository is public, so the preferred install path is a direct terminal bootstrap command.

## True Bootstrap Commands

### macOS / Linux

Interactive install:

```bash
curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.sh | sh
```

Default install:

```bash
curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.sh | sh -s -- --defaults
```

### Windows PowerShell

Interactive install:

```powershell
irm https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.ps1 | iex
```

Default install:

```powershell
$env:GOV_AGENTIC_INSTALL_ARGS='-Defaults'; irm https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.ps1 | iex
```

## Fallback Clone Path

If you prefer cloning first:

### macOS / Linux

```bash
git clone https://github.com/dendyadinirwana/gov-agentic-AI.git
cd gov-agentic-AI
./install.sh --target-dir .
```

### Windows PowerShell

```powershell
git clone https://github.com/dendyadinirwana/gov-agentic-AI.git
cd gov-agentic-AI
./install.ps1 -TargetDir .
```


## Interactive Checklist UX

The installer prompts use typed values instead of requiring numeric menu choices. For cluster activation, the installer displays a checklist and lets users toggle clusters by typing a cluster name or prefix.

Useful cluster commands:

- `all` activates every cluster.
- `none` clears the checklist.
- `done` accepts the current checklist.
- Enter accepts the current checklist.

## Runtime Discovery

When you choose a runtime such as `hermes`, `openclaw`, `codex`, `claude`, or `antigravity`, the installer scans common macOS/Linux/Windows runtime config locations and records the result in `configs/runtime.generated.json`.

The installer does not write external runtime folders by default. It generates repo-local config plus advisory target paths so the selected runtime can mount or import the config safely.

## Supported Installer Options

- `--defaults`
- `--runtime <openclaw|hermes|codex|claude|antigravity|generic>`
- `--memory <local|mem9|hybrid>`
- `--governance <sandbox|production>`
- `--clusters <comma,separated,clusters>`

PowerShell equivalents:

- `-Defaults`
- `-Runtime <openclaw|hermes|codex|claude|antigravity|generic>`
- `-Memory <local|mem9|hybrid>`
- `-Governance <sandbox|production>`
- `-Clusters <comma,separated,clusters>`

## Example

macOS/Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.sh | sh -s -- \
  --defaults \
  --runtime hermes \
  --memory hybrid \
  --governance production \
  --clusters tata-usaha,perencanaan-dan-anggaran,kebijakan-dan-hukum
```

Windows PowerShell:

```powershell
$env:GOV_AGENTIC_INSTALL_ARGS='-Defaults -Runtime hermes -Memory hybrid -Governance production -Clusters tata-usaha,perencanaan-dan-anggaran,kebijakan-dan-hukum'; irm https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.ps1 | iex
```
