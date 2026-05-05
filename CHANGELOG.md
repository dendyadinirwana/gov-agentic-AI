# Changelog

All notable changes to this repository will be documented in this file.

The format is inspired by Keep a Changelog, adapted for a practical MVP workflow.

## [0.1.0] - 2026-05-05

### Added
- Canonical role registry in `configs/role_registry.json`
- Registry-driven decision engine and orchestrator flow
- Formal A2A contracts for handoff, response, audit event, and terminal state
- Role runner abstraction and runtime adapter layer
- Real-runtime command bridge modes for Hermes/OpenClaw-style integration
- Audit taxonomy for governance, fallback, review, and runtime issues
- A2A unit tests and smoke tests
- Architecture documentation for A2A contracts and runtime behavior
- Sample first-slice request under `examples/agent-to-agent/`

### Changed
- Routing policy moved out of hardcoded script maps into registry-backed config
- Intent detection moved into declarative routing policy
- Action level, sensitivity, impact, and work-state logic moved toward declarative policy
- Installer/runtime packaging updated to treat `role_registry.json` as a first-class artifact
- README rewritten to reflect current GitHub-facing MVP state

### Validation
- `python3 -m unittest discover -s tests -v` passes
- `python3 scripts/smoke_test_agent_to_agent.py` passes
- `python3 scripts/verify_repo.py` passes during MVP stabilization phase

### MVP Scope
This release establishes the orchestration backbone MVP.

Included in MVP:
- governed request intake
- role-to-role handoff contracts
- audit event emission
- review-oriented terminal states
- local mock execution path
- command-bridge real runtime path

Not yet included in MVP:
- native runtime SDK integration
- production retrieval backend
- approval UI
- persistent audit store
- severity/retention/compliance automation beyond initial event labeling
