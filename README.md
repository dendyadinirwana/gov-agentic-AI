# Gov-Agentic AI

Government-oriented multi-role agent orchestration baseline with registry-driven routing, formal A2A contracts, governance gates, audit trails, and portable role skills.

> Current status: **MVP orchestration backbone is working**.

Gov-Agentic AI is not positioned as a generic chatbot wrapper. This repository is a structured foundation for building **governed agent-to-agent workflows** for public-sector work such as official drafting, compliance review, approval routing, escalation handling, and knowledge-assisted internal operations.

## Why this repo exists

Most AI prototypes for government fail for predictable reasons:
- routing logic is hardcoded and fragile
- role responsibilities drift across prompts, code, and docs
- human approval is treated as an afterthought
- auditability is too weak for real operational use
- runtime packaging differs from repo-local behavior

This repo tries to fix that by giving one reusable baseline with:
- canonical role registry
- declarative routing policy
- formal agent-to-agent contracts
- governance-aware decision engine
- runtime adapter layer
- validation and smoke tests

## Current MVP status

The current MVP is the **orchestration backbone**, not a full production deployment.

### What is working now
- canonical role metadata and routing backbone in `configs/role_registry.json`
- registry-driven orchestration through `scripts/agent_to_agent_orchestrator.py`
- registry-driven decision engine through `scripts/government_decision_engine.py`
- formal A2A contracts for:
  - handoff
  - response
  - audit event
  - terminal state
- role runner abstraction via `scripts/role_runner.py`
- runtime adapter layer via `scripts/role_runtime_adapter.py`
- safe mock execution path for local validation
- command-bridge real runtime path for Hermes/OpenClaw-style integration
- installer/runtime packaging alignment for canonical registry artifacts
- audit taxonomy for governance, review, fallback, and runtime issues
- unit tests and smoke validation

### What this MVP proves
This MVP proves that the repo can already support a governed flow like:
- intake by Yayak
- specialist drafting by Alfian
- compliance review by Edi
- terminal state with governance-aware review outcome
- audit event emission across the lifecycle

### What is not finished yet
This is **not yet** a full production system with:
- native Hermes runtime integration
- native OpenClaw runtime integration
- real retrieval / RAG layer over agency documents
- persistent audit storage backend
- approval UI / human review console
- policy-based alerting and escalation automation
- severity / retention classes for audit events

## Architecture at a glance

### 1. Canonical registry
Primary backbone:
- `configs/role_registry.json`

This file now acts as the main source of truth for:
- role metadata
- routing policy
- intent detection
- review routing
- action level, sensitivity, impact, and work-state policies

### 2. Decision engine
- `scripts/government_decision_engine.py`

This script reads registry-backed policy and computes:
- `intent_class`
- `action_level`
- `work_state`
- `decision_gate`
- `human_touchpoint_required`
- ownership and next-step context

### 3. Orchestrator
- `scripts/agent_to_agent_orchestrator.py`

This script coordinates:
- request intake
- role handoff creation
- role execution
- review routing
- terminal state generation
- audit event emission

### 4. A2A contract layer
Schemas:
- `schemas/agent_to_agent_handoff.schema.json`
- `schemas/agent_to_agent_response.schema.json`
- `schemas/agent_to_agent_audit_event.schema.json`
- `schemas/agent_to_agent_terminal_state.schema.json`

Validator:
- `scripts/a2a_contracts.py`

### 5. Runtime execution layer
- `scripts/role_runner.py`
- `scripts/role_runtime_adapter.py`

Supported runtime execution families:
- mock modes
  - `local-mock`
  - `hermes-mock`
  - `openclaw-mock`
- real command-bridge modes
  - `hermes-real`
  - `openclaw-real`

### 6. Validation layer
- `scripts/smoke_test_agent_to_agent.py`
- `scripts/verify_repo.py`
- `scripts/verify_runtime_config.py`
- `scripts/verify_runtime_pack.py`
- `scripts/verify_runtime_attach.py`
- `tests/`

## Repository highlights

### Role ecosystem
The repository models a 29-role government-oriented role ecosystem across multiple clusters, including:
- policy and legal
- planning and budget
- procurement
- data and analytics
- communications and documents
- HR and performance
- field/public coordination
- administrative operations
- escalation and conflict handling

Top orchestration role:
- **Yayak**

Current MVP baseline execution path:
- **Yayak → Alfian → Edi**

### Knowledge and skill packaging
The repo still includes the broader portable agent package structure:
- `skills/`
- `knowledge-base/`
- `prompts/`
- `schemas/`
- `configs/`

This means the MVP orchestration backbone sits inside a larger adoption kit for future runtime integration.

## Quickstart

### 1. Verify repo integrity
```bash
python3 scripts/verify_repo.py
```

### 2. Run the sample decision engine
```bash
python3 scripts/government_decision_engine.py \
  --input-json examples/agent-to-agent/yayak-alfian-edi.request.json \
  --pretty
```

### 3. Run the sample orchestrator
```bash
python3 scripts/agent_to_agent_orchestrator.py \
  --input-json examples/agent-to-agent/yayak-alfian-edi.request.json \
  --pretty
```

### 4. Run the smoke test
```bash
python3 scripts/smoke_test_agent_to_agent.py
```

### 5. Run the unit tests
```bash
python3 -m unittest discover -s tests -v
```

## Example MVP output behavior
For the first-slice sample flow, the expected behavior is currently:
- owner starts at `top-layer__gov-ai_yayak`
- intent resolves to `draft-formal-artifact`
- execution path is `Alfian -> Edi`
- final state is `needs_review`
- audit events include governance and human-touchpoint signals

## Audit and governance model
The current A2A audit taxonomy includes:
- `handoff_created`
- `role_response_recorded`
- `workflow_terminalized`
- `governance_gate_triggered`
- `human_touchpoint_required`
- `fallback_used`
- `runtime_failed`
- `runtime_timeout`
- `review_returned`

This improves traceability for:
- normal role execution
- governance review gates
- fallback behavior
- runtime failures
- review loops back to orchestrator

## Runtime notes
The real runtime path is currently **command-bridge based**.

That means this repo can already integrate with Hermes/OpenClaw-style runtimes if you provide runtime commands through config or environment variables, but it is **not yet a native SDK-level integration**.

This is intentional for the MVP phase:
- practical to wire
- easy to test locally
- avoids fake assumptions about runtime internals

## Key docs
- `docs/architecture/AGENT_TO_AGENT_CONTRACTS_AND_RUNTIME.md`
- `docs/architecture/A2A_RUNTIME_HARDENING.md`
- `docs/architecture/GOVERNMENT_WORK_LOGIC.md`
- `docs/architecture/REPO_CONTRACT.md`

## Recommended next steps after MVP
The most natural next milestones are:
1. native runtime hardening for Hermes/OpenClaw
2. audit severity / retention / compliance classes
3. golden fixtures for more workflow types
4. retrieval integration over real government documents
5. human approval / review interface

## Bottom line
If your question is:

**“Is there already an MVP here?”**

The honest answer is:

**Yes — the orchestration MVP is already here.**

If your question is:

**“Is this already a full production government AI platform?”**

The honest answer is:

**Not yet.**

But the backbone is now strong enough to commit, share, and iterate as a serious MVP branch on GitHub.
