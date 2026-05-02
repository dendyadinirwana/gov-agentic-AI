# Gov-Agentic AI Knowledge Authoring Guide

## Purpose
This guide defines how maintainers extend `knowledge-base/` without breaking role usability, source provenance, or cross-role consistency.

## Required Starter Artifacts Per Role
Every role folder under `knowledge-base/<cluster>/<role>/` must keep these starter artifacts current:
- `00-readme/role-charter.md`
- `01-source-documents/source-map.md`
- `02-regulations-and-policies/policy-map.md`
- `03-templates-and-examples/artifact-catalog.md`
- `04-sop-and-workflows/workflow-map.md`
- `04-sop-and-workflows/decision-boundaries.md`
- `05-reference-data/reference-catalog.md`
- `06-output-samples/starter-output-examples.md`
- `07-review-notes/quality-checklist.md`
- `08-ingestion-ready/intake-guide.md`
- `09-archive/archive-rules.md`

## Where Content Belongs
- `00-readme`: role charter, scope, non-scope, handoff boundaries.
- `01-source-documents`: source inventory, priority rules, provenance notes.
- `02-regulations-and-policies`: policy maps, decision-impacting checklists, interpretations.
- `03-templates-and-examples`: reusable templates and artifact catalog.
- `04-sop-and-workflows`: operating sequence, approval path, escalation triggers.
- `05-reference-data`: stable dictionaries, lookup tables, entity lists, status codes.
- `06-output-samples`: good exemplars and output shapes.
- `07-review-notes`: failure modes, reviewer heuristics, red flags.
- `08-ingestion-ready`: metadata rules and intake instructions.
- `09-archive`: superseded content with archival rationale.

## `_shared` vs Role-Local
Add knowledge to `knowledge-base/_shared/` when it is:
- canonical across multiple roles,
- a reusable control or audit pattern,
- a common dictionary or template shape,
- a policy hierarchy or shared governance rule.

Keep knowledge role-local when it changes:
- how one role decides,
- which inputs one role trusts first,
- what one role outputs,
- what one role must escalate.

Role-local guidance may override shared guidance only for role execution details. Shared canonical rules still win for governance, risk, audit, and cross-role controls.

## Provenance and Reviewability
For any new knowledge item, preserve:
- issuing owner
- issue date
- revision/version
- classification
- source type
- review status
- why the role needs it

Avoid adding unsourced copied prose. If the source is not reviewable, it should not become canonical repo knowledge.

## Updating Starter Content
When new role knowledge changes how the role should behave:
1. Update the raw document or note in the correct folder.
2. Refresh the starter artifact that points to it.
3. Re-run `python3 scripts/generate_role_knowledge.py --force` only if you intentionally want generated starter docs refreshed.
4. Re-run `python3 scripts/verify_knowledge_base.py` and `python3 scripts/verify_repo.py`.

## Archiving Rules
Move stale or superseded material into `09-archive/` when:
- a newer canonical source replaces it,
- a template is deprecated,
- an example is no longer safe or representative,
- a workflow is replaced.

Never archive the only active workflow map, the only current policy note, or the only usable output example without replacing it in the active folder first.
