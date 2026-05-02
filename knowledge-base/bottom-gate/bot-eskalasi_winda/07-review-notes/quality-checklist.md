# Quality Checklist — Bot Eskalasi (Winda)

## Pre-Release Review Checklist
- [ ] Role fit is correct for the request.
- [ ] Sources are named, current enough, and classified.
- [ ] Output uses the required contract structure.
- [ ] Assumptions are explicit and bounded.
- [ ] Confidence is not inflated beyond the evidence quality.
- [ ] Human touchpoint is named for consequential action.

## Common Failure Modes
- Wrong role keeps the task instead of routing or escalating.
- Template language is used without source grounding.
- Sensitive/public-impact content is drafted without approval path.
- Evidence map is omitted or too vague to audit.
- Example output is mistaken for official approval.

## Red-Flag Patterns
- unresolved role conflict
- blocked compliance/legal path
- missing human owner

## Reviewer Notes
- Prefer concise challenge notes over silent corrections.
- If you cannot explain why the output is safe, mark it low confidence and stop.
