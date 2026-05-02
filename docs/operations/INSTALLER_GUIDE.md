# Installer Guide

## Purpose
The Gov-Agentic AI installer creates a repo-local runtime activation config that tells an agent runtime: "you are now Gov-Agentic AI, Yayak is the default router, these clusters/roles/skills are active, and these governance rules apply."

The installer uses selective activation. It never deletes physical folders from `knowledge-base/`, `skills/`, `prompts/`, or `runtime-adapters/`; it only writes active selections into generated config files.

## Run

```bash
python3 scripts/install_gov_agentic_ai.py
```

Non-interactive defaults:

```bash
python3 scripts/install_gov_agentic_ai.py --defaults
```

Terminal bootstrap from GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.sh | sh
```

## Interactive Flow

### Runtime Target

The prompt uses names, not required numbers. Type a value such as `hermes`, `openclaw`, or press Enter for `generic`.

- `generic`: global portable mode for any runtime that can read repo files and `configs/runtime.generated.json`.
- `openclaw`: repo-mounted profile using `skills/skill_manifest.json`, active role skills, and role knowledge paths.
- `hermes`: persistent-agent profile with explicit local-vs-mem9 memory precedence.
- `codex`: local workspace profile with SKILL.md capability folders and verification scripts.
- `claude`: SKILL.md-compatible import profile with progressive disclosure references.
- `antigravity`: repo-mounted generic agent profile with manifest-driven routing.

### Memory Mode

- `local`: local `knowledge-base/` is canonical; no external memory is required.
- `mem9`: mem9 is the primary memory surface.
- `hybrid`: local `knowledge-base/` remains source of truth; mem9 stores preferences, session memory, and operational recall.

### Cluster Activation Checklist

Cluster selection is checklist-style:

- `[x]` means active.
- `[ ]` means inactive.
- Type a cluster name or prefix to toggle it.
- Type `all` to activate all clusters.
- Type `none` to clear selection.
- Type `done`, or press Enter, to accept the current checklist.

Example toggles:

```text
Selection: none
Selection: tata-usaha
Selection: kebijakan-dan-hukum
Selection: done
```

### Governance Mode

- `sandbox`: demo/testing mode. L4 still requires human approval; L3 can be explored as a draft or recommendation. Use this for internal trials and runtime iteration.
- `production`: strict HITL, audit, and data-classification enforcement. L3 and L4 require human approval. Use this for serious pilots and formal workflow integration.

## Runtime Discovery

When a specific runtime is selected, the installer scans common OS-specific runtime homes and records the result in `runtime_discovery`.

Examples:

- macOS Hermes: `~/Library/Application Support/Hermes`, `~/.hermes`, `~/.config/hermes`
- Linux Hermes: `~/.config/hermes`, `~/.hermes`
- Windows Hermes: `%APPDATA%/Hermes`, `%USERPROFILE%/.hermes`
- Codex: `${CODEX_HOME}` or `~/.codex`

Discovery statuses:

- `found`: a matching runtime folder exists.
- `not_found`: no runtime folder exists; repo-local config is still generated.
- `not_required`: `generic` mode does not need an external runtime home.

By default, the installer is advisory and safe: it does not write into external runtime folders. It writes repo-local config and recommends where a runtime config could be copied or mounted.

## Output Files

- `configs/runtime.generated.json`: machine-readable runtime config.
- `configs/active.deployment.yaml`: human-readable active deployment summary.

Key config sections:

- `runtime_target`: selected target runtime.
- `runtime_discovery`: OS and runtime-home scan results.
- `runtime_config_targets`: repo-local and recommended runtime config locations.
- `memory_policy`: local, mem9, or hybrid memory behavior.
- `active_clusters`, `active_roles`, `active_skills`: selective activation result.
- `human_approval_required_for`: governance enforcement levels.

## Validate

```bash
python3 scripts/verify_runtime_config.py configs/runtime.generated.json
python3 scripts/verify_repo.py
python3 scripts/verify_skills.py
```

## Example

```bash
python3 scripts/install_gov_agentic_ai.py \
  --defaults \
  --runtime hermes \
  --memory hybrid \
  --governance production \
  --clusters tata-usaha,perencanaan-dan-anggaran,kebijakan-dan-hukum
```
