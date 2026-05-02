---
name: gov-agentic-common
description: "Use this shared Gov-Agentic AI skill for action-level policy, data classification, HITL gates, audit logging, confidence handling, and common guardrails across all government role skills."
---

# Gov-Agentic Common Guardrails

## Purpose
Provide shared policy for all Gov-Agentic AI role skills. This skill is not a replacement for a role skill; it supplies common decision gates and output integrity rules.

## Use When
Use when a request involves government documents, public-sector decisions, sensitive/internal data, formal drafting, legal/fiscal/procurement impact, audit requirements, or cross-role escalation.

## Core Rules
- Humans retain formal authority.
- L3/L4 actions require Human-in-the-Loop approval.
- Sensitive data requires restricted handling and access audit.
- Claims need evidence maps.
- Low evidence means low confidence, not confident guessing.
- Conflicts escalate through the conflict matrix or Bot Eskalasi/Winda.

## References
- `references/action-level-policy.md`
- `references/data-classification.md`
- `references/hitl-and-audit.md`
