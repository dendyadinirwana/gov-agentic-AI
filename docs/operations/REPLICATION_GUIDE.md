# Replication Guide

## Goal
Clone this repository as the baseline for another Gov-Agentic AI deployment.

## Copy and Adapt
1. Fork/clone this repo.
2. Preserve directory contracts under `knowledge-base/`, `prompts/`, and `schemas/`.
3. Replace example documents with agency-specific sources.
4. Keep audit log fields compatible unless there is a controlled schema version bump.
5. Review role aliases and adapt only if the orchestration layer is updated consistently.

## Minimum Production Checklist
- System prompt reviewed
- Role inventory approved
- Shared knowledge ingested
- Role folders populated
- Data classification enforced
- Human approval gates connected
- Audit logging active
- Acceptance tests executed
