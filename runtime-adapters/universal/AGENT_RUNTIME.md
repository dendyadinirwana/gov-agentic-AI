# Universal Agent Runtime Adapter

This adapter explains how any compatible agent runtime should adopt this repository.

## Identity
The runtime should treat this repository as a Gov-Agentic AI deployment package.

## Required Inputs
- `configs/runtime.generated.json`
- `prompts/system/YayakAI_Master_System_Prompt_v3.0.md`
- `skills/_shared/gov-agentic-common/SKILL.md`
- selected active role skills
- selected active role knowledge

## Required Behavior
- default to Yayak as router
- use only active roles and active skills
- obey data classification and HITL policy
- emit the required output contract fields

## Decision Engine
- Initialize the government decision engine before route selection.
- Use the engine output to set `intent_class`, `work_state`, `document_status`, `current_owner_role`, `next_owner_role`, and `decision_gate`.
- Treat `HOLD`, `REVIEW_NEEDED`, and `ESCALATE_TO` as runtime control signals, not advisory prose only.
- Use `decision_engine.default_mode=gating` for stricter production behavior.
