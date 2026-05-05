# Gov-Agentic AI

Government-oriented multi-agent orchestration baseline for governed public-sector workflows.

Gov-Agentic AI is a repository for building **agent-to-agent (A2A) workflows** that are auditable, role-aware, governance-aware, and practical to integrate with runtimes such as **Hermes** and **OpenClaw**. Instead of treating AI as a single chatbot, this repo models structured work across roles, review gates, evidence, audit events, retrieval context, and human approval.

> **Current status:** MVP orchestration backbone is working and runnable locally.

---

## What this repo is

This repo is a foundation for government knowledge-work automation where output quality, routing discipline, approval boundaries, and traceability matter.

It is designed for workflows such as:
- official drafting and internal memo preparation
- compliance and legal review
- planning and budget review
- procurement neutrality checks
- archive and administrative routing
- escalation handling
- retrieval-grounded internal support work
- human-in-the-loop (HITL) approvals for consequential actions

This is **not** a generic chatbot wrapper and **not yet** a full production government AI platform. It is a serious MVP architecture for governed orchestration.

---

## Why this repo exists

Many AI prototypes fail in government settings for predictable reasons:
- routing logic is hardcoded and brittle
- role boundaries drift between prompts, code, and docs
- review and approval are bolted on too late
- evidence provenance is weak or missing
- audit trails are too thin for operational trust
- local demos do not map cleanly to actual runtime integration

Gov-Agentic AI addresses that with a reusable baseline built around:
- a canonical role registry
- registry-driven decision logic
- formal A2A contracts
- governance gates and review states
- runtime adapter patterns for Hermes/OpenClaw
- retrieval-backed evidence injection
- HITL review packet and decision flow
- validation and regression fixtures

---

## What is working today

The current MVP already includes:
- canonical role metadata and routing backbone in `configs/role_registry.json`
- registry-driven decision engine in `scripts/government_decision_engine.py`
- registry-driven orchestration in `scripts/agent_to_agent_orchestrator.py`
- formal A2A contracts for:
  - handoff
  - response
  - audit event
  - terminal state
  - HITL review decision
- runtime execution via:
  - mock modes
  - command-bridge runtime adapters for Hermes/OpenClaw-style execution
- audit taxonomy with governance and runtime failure handling
- retrieval-backed workflow grounding via local corpus adapter
- human-in-the-loop pause / packet / decision / resume flow
- fixture-backed regression tests and smoke validation

---

## What this MVP proves

This repository now proves a practical governed workflow architecture with:
- **multi-role orchestration**
- **review-aware terminal states**
- **retrieval-backed evidence flow**
- **auditable human review actions**
- **runtime portability patterns**

A representative governed path already works like this:
1. **Yayak** accepts and classifies the request
2. **Alfian** drafts or structures the work artifact
3. **Edi** performs compliance-oriented review
4. the workflow pauses for **human approval** when needed
5. the final state records governance, evidence, audit events, and review outcome

---

## What is not finished yet

This repo is still an MVP and not yet a full production platform with:
- native SDK-level Hermes integration
- native SDK-level OpenClaw integration
- real enterprise retrieval over live agency documents
- persistent audit storage backend
- production-grade web governance console
- policy-based alerting and escalation automation
- deployment packaging for institutional environments

That said, the backbone is now strong enough for:
- GitHub publication
- technical demos
- architecture reviews
- controlled pilots
- integration planning

---

## Architecture at a glance

### 1) Canonical role registry
**File:** `configs/role_registry.json`

Acts as the main source of truth for:
- role metadata
- routing policy
- intent mapping
- review routing
- action level, sensitivity, and work-state policy

### 2) Government decision engine
**File:** `scripts/government_decision_engine.py`

Computes workflow policy context such as:
- `intent_class`
- `action_level`
- `work_state`
- `decision_gate`
- `human_touchpoint_required`
- ownership and next-step context

### 3) A2A orchestrator
**File:** `scripts/agent_to_agent_orchestrator.py`

Coordinates:
- request intake
- role handoff creation
- role execution
- review routing
- audit event emission
- terminal state generation
- workflow resume after human review decision

### 4) Formal contract layer
**Schemas:**
- `schemas/agent_to_agent_handoff.schema.json`
- `schemas/agent_to_agent_response.schema.json`
- `schemas/agent_to_agent_audit_event.schema.json`
- `schemas/agent_to_agent_terminal_state.schema.json`
- `schemas/hitl_review_decision.schema.json`

**Validator:**
- `scripts/a2a_contracts.py`

### 5) Runtime adapter layer
**Files:**
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

### 6) Retrieval grounding layer
**Files:**
- `scripts/local_retriever.py`
- `configs/retrieval.generated.json`
- `examples/retrieval-corpus/government_sources.json`

Provides:
- deterministic local retrieval
- query term derivation
- evidence source normalization
- provenance preservation in workflow outputs

### 7) Human-in-the-loop review layer
**Files:**
- `scripts/hitl_review_console.py`
- `schemas/hitl_review_decision.schema.json`

Provides:
- review packet generation
- reviewer decision contract
- resume/finalize workflow path
- auditable human review actions

---

## Repo highlights

### Role ecosystem
The repository models a 29-role government-oriented ecosystem across multiple clusters, including:
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

Representative MVP path:
- **Yayak -> Alfian -> Edi**

### Portable agent package structure
The orchestration backbone sits inside a broader adoption kit that still includes:
- `skills/`
- `knowledge-base/`
- `prompts/`
- `schemas/`
- `configs/`

That makes this repo useful not only as a codebase, but also as a portable operating model for future runtime integration.

---

## Quickstart

### 1) Verify repo integrity
```bash
python3 scripts/verify_repo.py
```

### 2) Run the decision engine
```bash
python3 scripts/government_decision_engine.py \
  --input-json examples/agent-to-agent/yayak-alfian-edi.request.json \
  --pretty
```

### 3) Run the orchestrator
```bash
python3 scripts/agent_to_agent_orchestrator.py \
  --input-json examples/agent-to-agent/yayak-alfian-edi.request.json \
  --pretty
```

### 4) Run smoke tests
```bash
python3 scripts/smoke_test_agent_to_agent.py
python3 scripts/smoke_test_agent_to_agent_matrix.py
```

### 5) Run unit tests
```bash
python3 -m unittest discover -s tests -v
```

### 6) Run a retrieval-backed flow
```bash
python3 scripts/agent_to_agent_orchestrator.py \
  --input-json examples/agent-to-agent/retrieval-budget-review.request.json \
  --pretty
```

### 7) Run a HITL review flow
Generate workflow:
```bash
python3 scripts/agent_to_agent_orchestrator.py \
  --input-json examples/agent-to-agent/hitl-review.request.json \
  --pretty
```

Generate review packet:
```bash
python3 scripts/hitl_review_console.py packet \
  --workflow-json /path/to/workflow.json \
  --output-json /path/to/review-packet.json
```

Generate human decision:
```bash
python3 scripts/hitl_review_console.py decide \
  --packet-json /path/to/review-packet.json \
  --decision approve \
  --actor-id reviewer-1 \
  --actor-role human-reviewer \
  --display-name "Reviewer Internal" \
  --notes "Dapat dilanjutkan" \
  --output-json /path/to/review-decision.json
```

Resume/finalize workflow:
```bash
python3 scripts/agent_to_agent_orchestrator.py \
  --input-json examples/agent-to-agent/hitl-review.request.json \
  --review-decision-json /path/to/review-decision.json \
  --pretty
```

---

## Baseline A2A fixtures

Current regression fixtures under `examples/agent-to-agent/`:
- `yayak-alfian-edi.request.json` — formal draft plus legal/compliance review path
- `budget-review.request.json` — budget review path via **Anastasia**
- `procurement-neutrality.request.json` — procurement neutrality path via **Hafidus**
- `archive-record.request.json` — archive preparation path via **Sovia -> Izza**
- `escalation-blocker.request.json` — escalation blocker path via **Winda** with terminal `needs_review`
- `retrieval-budget-review.request.json` — retrieval-backed budget review path with provenance from local corpus
- `hitl-review.request.json` — HITL path via **Alfian -> Edi** with review packet, decision, and resume flow

Validation helpers:
- `python3 scripts/smoke_test_agent_to_agent.py`
- `python3 scripts/smoke_test_agent_to_agent_matrix.py`

---

## Audit and governance model

The audit taxonomy currently covers:
- `handoff_created`
- `role_response_recorded`
- `workflow_terminalized`
- `governance_gate_triggered`
- `human_touchpoint_required`
- `fallback_used`
- `runtime_failed`
- `runtime_timeout`
- `review_returned`
- `human_review_decision`
- `workflow_resumed`

This improves traceability for:
- normal role execution
- governance review gates
- fallback behavior
- runtime incidents
- review loops back to orchestrator
- human approval actions
- workflow resume/finalization after review

---

## Hermes / OpenClaw integration stance

The current runtime path is intentionally **command-bridge based**, not fake-native.

That means the repo can already integrate with Hermes/OpenClaw-style runtimes through explicit runtime commands and adapters, while staying honest about MVP boundaries.

Why this matters:
- practical to wire locally
- deterministic to test
- avoids pretending to have a native runtime SDK integration that does not yet exist
- gives a clean migration path toward deeper runtime coupling later

---

## Install or load skills via AI prompt

This repo also works well as a source of portable skills and governed workflow assets. If you want another AI agent to **install or load a skill** from this repo, the safest pattern is to use a **prompt command** rather than a blind shell installer.

### Hermes prompt template
Use this when asking a Hermes-based agent to install or load a skill from a repo or shared skill directory.

```text
You are operating Hermes Agent on my machine.

Task:
Install or load the skill named "<SKILL_NAME>" from this source:
- repo path or URL: <SOURCE_PATH_OR_URL>

Requirements:
1. Inspect the skill first before installing.
2. If the source is a direct SKILL.md URL, use Hermes native skill install flow.
3. If the source is a local/shared skill directory, make it available through Hermes using the cleanest native path:
   - prefer `skills.external_dirs` in Hermes config for shared libraries
   - avoid duplicating files unless necessary
4. Verify the skill is discoverable with Hermes after setup.
5. Report back with:
   - install/load method used
   - final skill name
   - config changes made
   - verification result

Preferred Hermes commands:
- `hermes skills inspect <ID_OR_URL>`
- `hermes skills install <ID_OR_URL>`
- `hermes config set skills.external_dirs[0] <ABSOLUTE_PATH>` or equivalent config edit when using shared dirs
- `hermes skills list`

Do not fabricate success. Verify the result.
```

### OpenClaw prompt template
Use this when asking an OpenClaw-style agent to make a repo skill available while keeping migration hygiene.

```text
You are operating an OpenClaw-style local agent environment.

Task:
Make the skill named "<SKILL_NAME>" available from this source:
- repo path or URL: <SOURCE_PATH_OR_URL>

Requirements:
1. Inspect the skill structure first.
2. Prefer a shared-library or workspace-native path instead of copying random files blindly.
3. If this should be shared with Hermes too, preserve a clean cross-agent skill path such as:
   - /Users/dendyadinirwana/.agents/skills
4. If migration to Hermes compatibility is relevant, keep the skill layout compatible with a standard `SKILL.md`-based structure.
5. Verify the skill is actually discoverable after setup.
6. Report back with:
   - chosen install/load path
   - whether files were copied, linked, or referenced
   - any compatibility risks
   - verification result

Do not claim success without verification.
```

### Practical example for a shared skill library
If the skill already lives in a shared folder like `~/.agents/skills`, the best prompt is usually this:

```text
Configure Hermes to discover skills from `/Users/dendyadinirwana/.agents/skills` using `skills.external_dirs`, then verify that the skill `<SKILL_NAME>` is visible through Hermes skill discovery. Do not duplicate the skill unless native discovery fails.
```

---

## Key docs
- `docs/architecture/AGENT_TO_AGENT_CONTRACTS_AND_RUNTIME.md`
- `docs/architecture/A2A_RUNTIME_HARDENING.md`
- `docs/architecture/A2A_RETRIEVAL_INTEGRATION.md`
- `docs/architecture/A2A_HITL_REVIEW_CONSOLE.md`
- `docs/architecture/GOVERNMENT_WORK_LOGIC.md`
- `docs/architecture/REPO_CONTRACT.md`

Legacy installer/runtime-packaging materials that are no longer part of the active MVP surface have been moved to `APUS DONG/`.

---

## Recommended next steps

The most natural next phases are:
1. native Hermes runtime hardening
2. native OpenClaw runtime hardening
3. real retrieval over live government document stores
4. persistent audit backend
5. governance web console
6. deployment packaging for institutional pilots

---

## Bottom line

If the question is:

**"Is there already an MVP here?"**

The honest answer is:

**Yes. The orchestration MVP is already here.**

If the question is:

**"Is this already a production-grade government AI platform?"**

The honest answer is:

**Not yet.**

But the repo is now strong enough to share, demo, review, and extend as a serious Gov-Agentic AI foundation.
