# Boot Sequence

1. Read `configs/runtime.generated.json`.
2. Load `prompts/system/YayakAI_Master_System_Prompt_v3.0.md`.
3. Load `skills/_shared/gov-agentic-common/SKILL.md`.
4. Default the orchestrator identity to Yayak.
5. Restrict routing to `active_roles` and `active_skills`.
6. Retrieve from local role knowledge and shared knowledge.
7. Apply memory behavior from `memory_mode`.
8. Emit outputs with evidence map, confidence, red flags, human touchpoint, and next step.
9. Require HITL for configured approval levels.
