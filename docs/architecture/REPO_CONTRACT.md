# Repository Contract

This repository is the canonical baseline for replicating Gov-Agentic AI.

## Stable Contracts
- `knowledge-base/kb_manifest.json` is the machine-readable role inventory.
- `knowledge-base/_shared` is the shared knowledge root.
- `knowledge-base/<cluster>/<role>/_shared-links` contains symlinks to shared knowledge.
- `prompts/system/YayakAI_Master_System_Prompt_v3.0.md` is the root orchestration prompt.
- `schemas/audit_log_template_v3.0.json` is the minimum audit log contract.
- `schemas/Gov_Agentic_AI_v3.1_Acceptance_Tests.json` is the minimum acceptance test suite.

## Change Rules
- Do not rename role folders without updating `kb_manifest.json`.
- Do not remove audit fields without schema version bump.
- Do not duplicate shared documents into many role folders; use `_shared` and symlinks.
- Do not allow role-specific prompts to bypass Yayak routing, HITL, data classification, or audit logging.
