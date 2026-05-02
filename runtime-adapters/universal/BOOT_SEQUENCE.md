# Boot Sequence

If the runtime starts from the repository root, read `AGENT_README.md` first to understand identity, routing posture, and governance behavior.

1. Read `configs/runtime.generated.json`.
2. Load `prompts/system/YayakAI_Master_System_Prompt_v3.0.md`.
3. Load `skills/_shared/gov-agentic-common/SKILL.md`.
4. Load `docs/architecture/GOVERNMENT_WORK_LOGIC.md`, `schemas/government_workflow_state.schema.json`, `configs/government_logic_rules.json`, and `configs/authority_matrix.json`.
5. Initialize the government decision engine from `scripts/government_decision_engine.py` or the configured `decision_engine_entrypoint`.
6. Default the orchestrator identity to Yayak.
7. For each request, run the decision engine before specialist routing.
8. Restrict routing to `active_roles` and `active_skills`.
9. Retrieve from local role knowledge and shared knowledge.
10. Apply memory behavior from `memory_mode`.
11. Emit outputs with evidence map, confidence, red flags, human touchpoint, and next step.
12. Require HITL for configured approval levels and any `REVIEW_NEEDED`, `HOLD`, or `ESCALATE_TO` gate from the decision engine.
