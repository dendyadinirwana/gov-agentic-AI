# Universal Agent Runtime Adapter

Start with `AGENT_README.md` at the repository root. This file is the single behavioral entrypoint; adapter docs only translate that contract into runtime-specific layout and boot expectations.

This adapter explains how any compatible agent runtime should adopt this repository.

## Identity
The runtime should treat this repository as a Gov-Agentic AI deployment package.

## Required Inputs
- `AGENT_README.md`
- `runtime-adapters/universal/RUNTIME_HANDSHAKE.md`
- `examples/BOOTSTRAP_EXAMPLE.json`
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

## Machine-Readable Bootstrap Contract
- Read `agent_entrypoint` from `configs/runtime.generated.json` and resolve it before any task execution.
- Materialize bootstrap state for identity, active roles, active skills, governance mode, memory mode, and decision-engine settings.
- If bootstrap state is incomplete, fail closed instead of routing as a generic assistant.
