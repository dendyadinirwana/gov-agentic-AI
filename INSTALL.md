# Install Gov-Agentic AI from Terminal

This repository is currently **private**. For private repositories, `raw.githubusercontent.com` URLs return `404` unless the request is authenticated, so the recommended install path uses GitHub CLI (`gh`).

## Prerequisites

- Git
- Python 3
- GitHub CLI authenticated to the account that can access this private repo

Check auth:

```bash
gh auth status
```

## Private Repo Install Commands

### macOS / Linux

Interactive install:

```bash
gh repo clone dendyadinirwana/gov-agentic-AI && cd gov-agentic-AI && ./install.sh --target-dir .
```

Default install:

```bash
gh repo clone dendyadinirwana/gov-agentic-AI && cd gov-agentic-AI && ./install.sh --target-dir . --defaults
```

### Windows PowerShell

Interactive install:

```powershell
gh repo clone dendyadinirwana/gov-agentic-AI; cd gov-agentic-AI; ./install.ps1 -TargetDir .
```

Default install:

```powershell
gh repo clone dendyadinirwana/gov-agentic-AI; cd gov-agentic-AI; ./install.ps1 -TargetDir . -Defaults
```

## If the Repo Becomes Public

Only if this repository is public, macOS/Linux can use a raw script pipe:

```bash
curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.sh | sh
```

Default mode if public:

```bash
curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.sh | sh -s -- --defaults
```

Windows public raw mode:

```powershell
irm https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.ps1 | iex
```

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
gh repo clone dendyadinirwana/gov-agentic-AI && cd gov-agentic-AI && ./install.sh --target-dir . \
  --defaults \
  --runtime hermes \
  --memory hybrid \
  --governance production \
  --clusters tata-usaha,perencanaan-dan-anggaran,kebijakan-dan-hukum
```

Windows PowerShell:

```powershell
gh repo clone dendyadinirwana/gov-agentic-AI; cd gov-agentic-AI; ./install.ps1 -TargetDir . -Defaults -Runtime hermes -Memory hybrid -Governance production -Clusters tata-usaha,perencanaan-dan-anggaran,kebijakan-dan-hukum
```
