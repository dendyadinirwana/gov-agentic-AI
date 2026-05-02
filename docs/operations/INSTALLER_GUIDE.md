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
