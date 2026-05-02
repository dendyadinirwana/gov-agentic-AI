# Artifact Catalog — GOV-AI (Yayak)

## Primary Artifacts
- routing decision
- intent classification
- action-level decision
- handoff plan
- cross-role coordination brief
- escalation gating note

## Role-Local Template Patterns
### Router Decision Card
Use when a task first arrives and must be classified.
- task summary
- inferred intent
- data classification
- action level
- primary route
- consulted roles
- human touchpoint

### Multi-Role Handoff Brief
Use when a workflow spans multiple roles.
- workflow name
- step-by-step route
- required evidence by role
- risk flags
- reviewer chain
- stop conditions

### Escalation Gate Memo
Use when the task cannot continue safely.
- blocker description
- failed control or missing owner
- impact area
- escalation target
- resume condition

## Minimum Artifact Metadata
- source reference(s)
- version or revision date
- drafter role and reviewer role
- action level / impact level
- status: draft, review, hold, approved, archived
- trace_id

## Consumption Notes
- Router artifacts must optimize for clarity and replayability, not prose polish.
- Every route should make it obvious why Yayak chose the path and where humans re-enter control.
- If the route is novel, store the pattern in `../08-ingestion-ready/` for future reuse.
