# Gov-Agentic AI Skills

This folder contains universal `SKILL.md` skills for Gov-Agentic AI role replication across Claude, Codex, OpenClaw, Hermes Agent, and Antigravity-style agent runtimes.

## Structure
- `roles/` contains 29 role skills.
- `_shared/gov-agentic-common` contains shared guardrails.
- `skill_manifest.json` is the machine-readable registry.

## Usage
Install or import the role skill folder required by the target runtime. Each role skill points back to this repo's prompts and knowledge-base paths instead of duplicating large knowledge documents.

## Validation
Run:

```bash
python3 scripts/verify_skills.py
```
