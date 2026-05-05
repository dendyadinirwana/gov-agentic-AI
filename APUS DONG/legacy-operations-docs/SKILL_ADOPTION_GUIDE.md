# Skill Adoption Guide

## Purpose
This guide explains how to adopt the 29 Gov-Agentic AI role skills across Claude, Codex, OpenClaw, Hermes Agent, Antigravity, or another agent runtime that supports `SKILL.md`-style capability folders.

## Runtime Contract
Each role skill is self-contained enough to route and execute role-specific tasks, but it intentionally does not duplicate large knowledge files. The skill points to:
- role prompt under `prompts/roles`
- role knowledge under `knowledge-base/<cluster>/<role>`
- shared knowledge under `_shared-links`
- shared guardrails under `skills/_shared/gov-agentic-common`

## Adoption Steps
1. Import or mount `skills/_shared/gov-agentic-common`.
2. Import or mount the needed role folders from `skills/roles`.
3. Preserve repository-relative paths or update `skills/skill_manifest.json` consistently.
4. Connect the runtime retrieval layer to `knowledge-base` and `_shared-links`.
5. Enforce audit output using `schemas/audit_log_template_v3.0.json`.
6. Validate routing and behavior using `schemas/Gov_Agentic_AI_v3.1_Acceptance_Tests.json`.

## Skill Selection Rule
- Use Yayak first for broad user requests, routing, intent classification, conflict detection, and action-level decisions.
- Use specialist role skills for domain drafting, analysis, review, and evidence-grounded outputs.
- Use monitor/compliance skills to challenge evidence, audit readiness, and red flags.
- Use Winda when conflict remains unresolved or a human takeover path must be selected.

## Validation
Run:

```bash
python3 scripts/generate_role_skills.py --check
python3 scripts/verify_skills.py
```

Expected:
- `role_count=29`
- `skill_count=29`
- `missing_skill_md=0`
- `invalid_frontmatter=0`
- `broken_reference_paths=0`
