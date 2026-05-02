# Quality Checklist — Analisis Statistik (Hanan)

## Pre-Release Review Checklist
- [ ] Dataset origin, structure, and assumptions are visible enough to justify the analysis.
- [ ] Method choice matches the question being asked.
- [ ] Result interpretation is separated from unsupported policy or causal claims.
- [ ] Caveats, confidence limits, and data-quality issues are explicit.
- [ ] Human touchpoint is named before consequential use.

## Common Failure Modes
- statistical language hides weak or biased data
- result is over-interpreted as policy fact or causal proof
- normalization/weighting assumptions are not disclosed
- draft looks precise but source provenance is missing
- uncertainty is suppressed to satisfy urgency

## Red-Flag Patterns
- small or partial data treated as complete truth
- outliers or missing values materially change interpretation
- requester pressures for certainty beyond the evidence
- output is likely to affect budget, policy, or public messaging without review

## Reviewer Notes
- Hanan should prefer careful caveats over false precision.
- If the data or method cannot be defended briefly, confidence should drop and escalation should be considered.
