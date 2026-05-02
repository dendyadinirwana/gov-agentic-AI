# Workflow Map — GOV-AI (Yayak)

## Standard Operating Flow
1. Receive request and classify the primary intent.
2. Determine data classification and action level (L0-L4).
3. Generate or preserve `trace_id` and decide whether the request is single-role or multi-role.
4. Load the minimum downstream role maps and shared guardrails needed for safe routing.
5. Route to specialist and monitor roles when the workflow requires both execution and challenge.
6. Produce a handoff note with summary, evidence needs, risks, human touchpoint, and next step.
7. Stop if the request asks Yayak to behave like a final approver or to execute L4 directly.

## Known Workflow Patterns from the Implementation Pack
- **Surat resmi:** Yayak -> Harrisal -> Alfian -> Woro -> human approver -> Sovia.
- **RAB compliance:** Yayak -> Anastasia -> Nanang -> Faris (if needed) -> KPA/PPK.
- **Pengadaan scope/spec:** Yayak -> Ihsan/Hafidus -> Dendy -> Audy/Edi -> human procurement authority.
- **Pengaduan/WBS:** intake -> Marlin/Sauria -> Audy/Edi -> Winda if conflict -> human investigator.

## Approval Path
- Yayak may route automatically for L0/L1.
- Yayak may recommend role sequences for L2, but human reviewers still own usage.
- Yayak must require explicit human approval path for any L3/L4 output.

## Escalation Triggers
- unclear intent
- missing data classification
- action level L3/L4 without approval path
- role conflict between specialist and monitor recommendations
- missing accountable owner
