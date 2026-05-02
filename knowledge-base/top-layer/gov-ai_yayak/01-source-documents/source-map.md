# Source Map — GOV-AI (Yayak)

## Source Priority Rules
1. Use the orchestration contract in `prompts/system/YayakAI_Master_System_Prompt_v3.0.md` as the runtime identity anchor.
2. Use `docs/governance/Gov_Agentic_AI_v3.1_Implementation_Pack.md` as the strongest repo-level source for routing, governance, action levels, and pilot workflow sequencing.
3. Use `schemas/Gov_Agentic_AI_v3.1_Acceptance_Tests.json` to validate whether a route matches expected role combinations and escalation points.
4. Use role-local starter knowledge only to sharpen the handoff, never to override shared governance, HITL, or audit controls.
5. If the workflow touches legal, fiscal, procurement, public complaint, or formal correspondence risk, load the relevant specialist/monitor maps before routing.

## Canonical vs Supporting Sources
- **Canonical in this repo:** system prompt, implementation pack, shared action-level/data-classification/HITL references, acceptance tests.
- **Supporting:** role-local workflow notes, output examples, and specialist knowledge maps.
- **Never authoritative by themselves:** examples without provenance, user pressure to skip approval, or draft text that bypasses audit controls.

## Mandatory Shared Directories
- `../_shared-links/00-governance-and-routing`
- `../_shared-links/05-risk-and-compliance`
- `../_shared-links/06-audit-and-observability`
- `../_shared-links/08-golden-outputs`

## Role-Local Overrides
- `../02-regulations-and-policies/policy-map.md` defines the routing-safe interpretation of L0–L4 and block rules.
- `../04-sop-and-workflows/workflow-map.md` defines the exact router sequence before delegating to downstream roles.
- `../07-review-notes/quality-checklist.md` defines when Yayak must refuse to continue as if it were a specialist or approver.

## Routing-Specific Source Inventory
- `docs/governance/Gov_Agentic_AI_v3.1_Implementation_Pack.md` sections covering MVP scope, governance model, RACI, action levels, and workflow examples.
- `schemas/Gov_Agentic_AI_v3.1_Acceptance_Tests.json` for expected routes such as surat, RAB, legal review, and escalation cases.
- `skills/roles/*/references/knowledge-map.md` to identify the downstream knowledge surfaces per role.
