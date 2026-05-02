# Output Contract

Use this structure for Penerjemah Kebijakan (Iqbal) outputs.

## Required Fields
- `summary`: concise answer or artifact summary.
- `evidence_map`: sources, dates, relevance, and gaps.
- `assumptions`: assumptions made and what would change them.
- `confidence_status`: High, Medium, or Low.
- `red_flags`: compliance, legal, fiscal, data, public, or operational risks.
- `human_touchpoint`: who must review, approve, reject, hold, or take over.
- `next_step`: proceed, revise, hold, escalate, block, or ask for source.

## Minimum Rule
If a required field cannot be completed, explicitly write `Not available` and explain the gap under `red_flags` or `assumptions`.
