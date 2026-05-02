# Installer Guide

## Purpose
The Gov-Agentic AI installer creates a runtime activation config without deleting repository content.

## Run

```bash
python3 scripts/install_gov_agentic_ai.py
```

Or use defaults/non-interactive mode:

```bash
python3 scripts/install_gov_agentic_ai.py --defaults
```

## What It Asks
- runtime target
- memory mode
- active clusters
- governance mode
- output config location

## Output Files
- `configs/runtime.generated.json`
- `configs/active.deployment.yaml`

## Behavior
- keeps the full repository intact
- activates clusters and roles through generated config only
- defaults to Yayak as router
- keeps L3/L4 approval rules in production mode

## Validate

```bash
python3 scripts/verify_runtime_config.py configs/runtime.generated.json
python3 scripts/verify_repo.py
python3 scripts/verify_skills.py
```

## Installer v2 Notes

Interactive choices now include inline explanations so users understand the operational impact before selecting.

### Governance Modes

- `sandbox`: demo/testing mode; L4 still requires human approval, while L3 can be explored as draft/recommendation. Use this for internal trials and prompt/runtime iteration.
- `production`: strict HITL, audit, and data-classification enforcement. L3 and L4 require human approval. Use this for real workflow pilots and formal deployments.

### Runtime Targets

- `generic`: global portable mode for any runtime that can read repo files and `configs/runtime.generated.json`.
- `openclaw`: repo-mounted profile using `skills/skill_manifest.json`, active role skills, and role knowledge paths.
- `hermes`: persistent-agent profile with explicit local-vs-mem9 memory precedence.
- `codex`: local workspace profile with SKILL.md capability folders and verification scripts.
- `claude`: SKILL.md-compatible import profile with progressive disclosure references.
- `antigravity`: repo-mounted generic agent profile with manifest-driven routing.

Runtime-specific behavior is now generated through `runtime-adapters/<runtime>/profile.json` and merged into `runtime.generated.json` under `runtime_adapter`, `runtime_paths`, and `runtime_overrides`.
