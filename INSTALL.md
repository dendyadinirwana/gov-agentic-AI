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

Update existing install:

```bash
curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.sh | sh -s -- --update
```

Doctor / health check:

```bash
curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/doctor.sh | sh
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

Update existing install:

```powershell
$env:GOV_AGENTIC_INSTALL_ARGS='-Update'; irm https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.ps1 | iex
```

Doctor / health check:

```powershell
irm https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/doctor.ps1 | iex
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

The installer detects canonical runtime homes first, then generates repo-local artifacts and can apply the managed central-home plus thin-shim install. For `generic`, the canonical global skill target is `~/.agents/skills/gov-agentic-ai`.

## MCP Auth Behavior

Default MCP mode is `local`. In that mode the generated config uses local stdio MCP only, with command-based servers such as `chrome-devtools-mcp`, and it does **not** emit `headers.Authorization` or prompt for an API key.

If you explicitly choose `remote` MCP mode, the installer asks for:

- remote MCP URL
- auth type: `none`, `bearer`, or `x-api-key`
- API key env var name only when authenticated access is selected

This keeps local MCP minimal, and keeps remote MCP explicit and reviewable.

## Supported Installer Options

- `--defaults`
- `--update`
- `--local-only`
- `--install-target-root <path>`
- `--runtime <openclaw|hermes|codex|claude|antigravity|generic>`
- `--memory <local|mem9|hybrid>`
- `--governance <sandbox|production>`
- `--clusters <comma,separated,clusters>`
- `--mcp-mode <local|remote>`
- `--mcp-url <https://...>`
- `--mcp-auth-type <none|bearer|x-api-key>`
- `--mcp-auth-env-var <ENV_VAR_NAME>`

PowerShell equivalents:

- `-Defaults`
- `-Update`
- `-Runtime <openclaw|hermes|codex|claude|antigravity|generic>`
- `-Memory <local|mem9|hybrid>`
- `-Governance <sandbox|production>`
- `-Clusters <comma,separated,clusters>`
- `-McpMode <local|remote>`
- `-McpUrl <https://...>`
- `-McpAuthType <none|bearer|x-api-key>`
- `-McpAuthEnvVar <ENV_VAR_NAME>`

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


## Runtime-Native Shim Exports

For runtime homes that benefit from a cleaner native surface, the installer now writes adapter-specific shim exports:

- Hermes: `hermes.runtime.config.yaml`
- OpenClaw: `openclaw.runtime.config.json`

These exports mirror the same canonical pointers as `runtime.generated.json`, but keep local MCP servers clean and omit empty auth scaffolding.

## Generated Runtime Pack

The installer now generates two artifacts: a central home pack under `build/central-home/<version>/` and a runtime shim pack under `build/runtime-pack/<runtime>/<version>/`.

Default behavior:

- generates repo-local full config
- generates `runtime-bootstrap.generated.json` as the minimal runtime startup artifact
- generates central-home and runtime-shim packs
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

## Doctor

Run the local doctor directly:

```bash
python3 scripts/doctor_gov_agentic_ai.py --runtime generic
```

Target a specific runtime shim:

```bash
python3 scripts/doctor_gov_agentic_ai.py --runtime hermes
```

The doctor runs repo verification, skill verification, runtime-config validation, and thin-shim attach validation. Use `--skip-repo`, `--skip-skills`, `--skip-config`, or `--skip-attach` to narrow the check surface.

Bootstrap doctor:

```bash
curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/doctor.sh | sh
```

PowerShell doctor:

```powershell
irm https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/doctor.ps1 | iex
```

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

Bootstrap uninstall:

```bash
curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/uninstall.sh | sh
```

PowerShell uninstall:

```powershell
irm https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/uninstall.ps1 | iex
```

## Update Mode

`--update` reuses the last installed runtime settings when possible, pulls the latest repo changes, rebuilds the central home and runtime shim, and preserves the current runtime target unless you explicitly override it.
