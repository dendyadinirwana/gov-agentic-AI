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

Before the wizard asks for runtime choices, it shows a welcome screen that explains what files will be written, what the installer will not modify, and how to start or exit safely.


The installer prompts are keyboard-first in interactive terminals. Runtime, memory, and governance prompts use ↑/↓ plus Enter. Cluster activation displays a checklist grouped by section; use ↑/↓ to move and Space to toggle. If the terminal does not support arrow keys, the installer falls back to typed values.

Useful cluster commands:

- ↑/↓ moves the highlight.
- Space toggles the highlighted cluster.
- `a` activates every cluster.
- `n` clears the checklist.
- Enter accepts the current checklist.
- `q` exits the installer gracefully.
- `Ctrl+C` force-stops immediately.

## Runtime Discovery

When you choose a runtime such as `hermes`, `openclaw`, `codex`, `claude`, or `antigravity`, the installer scans common macOS/Linux/Windows runtime config locations and records the result in `configs/runtime.generated.json`.

The installer does not write external runtime folders by default. It generates repo-local config plus advisory target paths so the selected runtime can mount or import the config safely. For `generic`, the advisory global skill target is `~/.agents/skills/gov-agentic-ai`.

## Supported Installer Options

- `--defaults`
- `--local-only`
- `--install-target-root <path>`
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


## Generated Runtime Pack

The installer now generates two artifacts: a central home pack under `build/central-home/<version>/` and a runtime shim pack under `build/runtime-pack/<runtime>/<version>/`.

Default behavior:

- generates repo-local config
- generates runtime pack
- installs by copy into the canonical runtime home unless `--local-only` is used

Canonical install topology:

- central canonical home: `~/.gov-agentic-ai/`
- runtime-specific thin shims attach to that central home

Runtime shim homes:

- `~/.hermes/gov-agentic-ai`
- `~/.openclaw/gov-agentic-ai`
- `~/.claude/gov-agentic-ai`
- `~/.codex/gov-agentic-ai`
- `~/.antigravity/gov-agentic-ai`
- `~/.agents/skills/gov-agentic-ai` for generic global skills

## Uninstall

Preview a managed uninstall:

```bash
python3 scripts/uninstall_gov_agentic_ai.py --runtime generic --dry-run
```

Remove a managed runtime install:

```bash
python3 scripts/uninstall_gov_agentic_ai.py --runtime generic --yes
```

See [`docs/operations/UNINSTALL_GUIDE.md`](./docs/operations/UNINSTALL_GUIDE.md) for runtime-specific uninstall notes and safety rules.
