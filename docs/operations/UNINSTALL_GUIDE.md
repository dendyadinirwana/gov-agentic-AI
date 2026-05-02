# Gov-Agentic AI Uninstall Guide

This repository remains the source clone, while `~/.gov-agentic-ai/` becomes the canonical installed home. By default uninstall removes only the managed runtime shim, not the repository clone or the central home.

## What Gets Removed
By default, the uninstall flow removes only the managed runtime home subtree:

- `~/.hermes/gov-agentic-ai`
- `~/.openclaw/gov-agentic-ai`
- `~/.claude/gov-agentic-ai`
- `~/.codex/gov-agentic-ai`
- `~/.antigravity/gov-agentic-ai`
- `~/.agents/skills/gov-agentic-ai`

It does **not** remove:

- this git repository clone
- role knowledge in the repo
- prompts in the repo
- source docs under `docs/`

## Safe CLI Usage
Preview first:

```bash
python3 scripts/uninstall_gov_agentic_ai.py --runtime generic --dry-run
```

Uninstall with confirmation:

```bash
python3 scripts/uninstall_gov_agentic_ai.py --runtime generic
```

Uninstall non-interactively:

```bash
python3 scripts/uninstall_gov_agentic_ai.py --runtime generic --yes
```

Also remove repo-local generated config files:

```bash
python3 scripts/uninstall_gov_agentic_ai.py --runtime generic --yes --remove-local-generated
```

## Safety Rules
The script refuses removal unless:

- target path ends in `gov-agentic-ai`
- target path looks like a managed install
- the target contains `install.receipt.json` or `runtime.generated.json`

This prevents deleting unrelated runtime folders by accident.

## Explicit Target Override
If needed, you can point to an explicit managed subtree:

```bash
python3 scripts/uninstall_gov_agentic_ai.py --target-root ~/.agents/skills/gov-agentic-ai --yes
```

Use this only for custom or test installs.

## Central Home Removal
To remove both the runtime shim and the canonical installed home:

```bash
python3 scripts/uninstall_gov_agentic_ai.py --runtime generic --yes --remove-central-home
```

## Bootstrap Uninstall

macOS/Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/uninstall.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/uninstall.ps1 | iex
```

Set flags through environment variables when needed, for example:

```bash
GOV_AGENTIC_UNINSTALL_ARGS="--runtime generic --yes --remove-central-home" curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/uninstall.sh | sh
```
