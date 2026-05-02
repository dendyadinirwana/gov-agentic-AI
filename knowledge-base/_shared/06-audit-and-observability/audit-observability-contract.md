# Audit and Observability Contract

## Minimum Audit Expectations
- trace_id preserved across routing and handoff
- output status recorded: draft, review, hold, approved, archived
- source references are visible enough for reconstruction
- human reviewer / approver is named for consequential outputs

## Observability Notes
Good runtime behavior is explainable, replayable, and bounded. If a role cannot show its source basis or handoff point, treat the output as low confidence.
