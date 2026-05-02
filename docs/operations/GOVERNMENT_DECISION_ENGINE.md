# Government Decision Engine

## Purpose
This draft engine makes the government-work logic executable. It classifies a request into a bureaucratic intent, infers a work state, resolves authority expectations, and emits a machine-readable gate decision.

## Inputs
The engine accepts either raw request text or an input JSON payload. Useful fields include:
- `request_text`
- `current_role_slug`
- `evidence_complete`
- `approval_owner_known`
- `material_impact`
- `sensitive`
- `intent_class` (optional override)
- `action_level` (optional override)

## Outputs
The engine returns a JSON object aligned with the government workflow schema plus runtime gate fields:
- `trace_id`
- `intent_class`
- `work_state`
- `current_owner_role`
- `next_owner_role`
- `action_level`
- `document_status`
- `required_evidence`
- `approval_gate`
- `stop_condition`
- `human_touchpoint_required`
- `decision_gate`
- `decision_reason`

## Gate Values
- `PROCEED`
- `REVIEW_NEEDED`
- `ESCALATE_TO`
- `HOLD`

## Example
```bash
python3 scripts/government_decision_engine.py \
  --request-text "buat surat undangan rapat koordinasi besok" \
  --current-role-slug top-layer__gov-ai_yayak \
  --pretty
```

## Intended Runtime Use
1. Receive a user request or work item.
2. Run the decision engine.
3. Route using `intent_class`, `work_state`, `current_owner_role`, and `next_owner_role`.
4. Stop or escalate when `decision_gate` is `HOLD` or `ESCALATE_TO`.
5. Require human review when `decision_gate` is `REVIEW_NEEDED`.

## Current Limits
- This is a draft heuristics engine, not a full policy parser.
- Role coverage in `configs/authority_matrix.json` is intentionally partial and should expand.
- The engine does not yet validate against the JSON Schema automatically; it emits a schema-shaped object.
