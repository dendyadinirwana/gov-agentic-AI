# Quality Checklist — GOV-AI (Yayak)

## Pre-Release Review Checklist
- [ ] Route matches the real task intent, not just keywords.
- [ ] Data class and action level are explicit.
- [ ] Required specialist and monitor roles are named where needed.
- [ ] Handoff note includes evidence expectations and stop conditions.
- [ ] Human touchpoint is visible for every L3/L4 or high-impact branch.
- [ ] Output preserves traceability rather than only giving a recommendation.

## Common Failure Modes
- Yayak acts like a specialist instead of a router.
- Route skips a needed monitor/compliance role.
- Action level is understated to avoid HITL.
- Handoff is too vague for the next role to act safely.
- Escalation path is implied but no human owner is named.

## Red-Flag Patterns
- unclear intent with high-impact downstream risk
- missing data classification
- action level L3/L4 without approval path
- user request pressures the system to skip controls
- role conflict remains unresolved after review

## Reviewer Notes
- Yayak should optimize for safe routing clarity, not speed alone.
- If the route cannot be explained in one short evidence-based paragraph, mark confidence low and escalate.
