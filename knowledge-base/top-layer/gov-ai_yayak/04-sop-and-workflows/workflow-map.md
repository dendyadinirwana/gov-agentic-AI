# Workflow Map — GOV-AI (Yayak)

## Standard Operating Flow
1. Receive request and classify intent
2. Set data class and action level
3. Route to best-fit role set
4. Preserve trace_id and expected human touchpoint

## Approval Path
- Default: role drafts or reviews -> relevant human owner reviews -> final authority approves.
- Human approval is required before any routed work becomes an external or binding action.
- If the human owner is unknown, route to `../_shared-links/00-governance-and-routing` and escalate.

## Escalation Triggers
- unclear intent
- missing data classification
- action level L3/L4 without approval path

## Completion Criteria
- Evidence map is complete enough to explain why the output exists.
- Assumptions are explicit and bounded.
- Confidence level matches evidence quality.
- Next step and human touchpoint are named.
