# Quality Checklist — Monitor SLA Tata Usaha (Izza)

## Pre-Release Review Checklist
- [ ] The case truly concerns service speed, backlog, aging, or admin throughput.
- [ ] SLA expectation is tied to a named workflow, service type, or disposition stage.
- [ ] Source timestamps and status evidence are visible enough to justify the alert.
- [ ] Pass/hold/escalate recommendation is proportional to the actual delay or risk.
- [ ] Human owner for remediation is named.

## Common Failure Modes
- SLA claim is made without timestamp or queue evidence.
- Monitor language quietly becomes operational approval.
- Backlog visibility ignores classification or dependency blockers.
- Red flag is raised but no accountable office is named.
- Escalation is triggered for normal variance with no service impact.

## Red-Flag Patterns
- repeated aging with no owner response
- disposition or letter queue crosses expected timeline
- request tries to suppress or rewrite service evidence
- backlog creates external or leadership-facing delay risk

## Reviewer Notes
- Izza should challenge with evidence, not just urgency language.
- If queue evidence is incomplete, mark confidence low and request timestamp reconciliation first.
