# Data Classification and Handling

- `public`: safe for normal drafting/search with standard logging
- `internal`: restricted to authenticated users with role-based access
- `restricted`: prefer private tenant/on-prem processing; mask before broader use
- `sensitive`: do not send to external model endpoints by default; require explicit approval and access audit
