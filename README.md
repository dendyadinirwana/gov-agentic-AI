# Gov-Agentic AI

**Production-ready repository baseline for building a government-grade agentic AI ecosystem with role orchestration, shared knowledge, auditability, Human-in-the-Loop control, and portable agent skills.**

This repository is designed as a **GitHub-first adoption package** for government digital transformation teams, AI engineers, solution architects, compliance reviewers, and agent-runtime implementers who need a reusable foundation for deploying **Gov-Agentic AI** safely and systematically.

## Executive Overview

Gov-Agentic AI is a structured multi-role agent ecosystem for public-sector work. It is not a generic chatbot wrapper. It is a **governed operating model** for AI-assisted government workflows such as drafting official documents, routing dispositions, reviewing legal and budget compliance, handling procurement-related checks, supporting data analysis, and escalating sensitive or high-impact tasks through formal human authority.

The design assumption is simple:

- AI may assist analysis, drafting, retrieval, and coordination.
- Humans retain formal authority, approval power, and accountability.
- Every important output should be traceable, reviewable, and auditable.
- Sensitive or high-impact actions must go through **Human-in-the-Loop (HITL)** gates.

This repo packages that model into reusable assets:

- a **role-based knowledge base**
- a **29-role skill ecosystem**
- prompts for orchestration and role execution
- audit schemas and acceptance tests
- governance and adoption documentation
- repo contracts for safe replication across runtimes

## What This Repository Provides

### 1. Government Role Orchestration

The repository models a **29-role Gov-Agentic AI ecosystem** across multiple government work clusters, including:

- policy and legal
- planning and budget
- procurement
- data and analytics
- communications and documents
- HR and performance
- field/public coordination
- administrative operations (*tata usaha*)
- escalation and conflict handling

At the top layer, **Yayak** acts as the orchestrator for intent classification, routing, action-level checks, and conflict-aware handoff.

### 2. Knowledge Base by Role

The repository includes a structured `knowledge-base/` designed for retrieval, ingestion, and long-term operational maintenance.

- `knowledge-base/_shared` holds cross-role canonical knowledge
- `knowledge-base/<cluster>/<role>` holds role-specific knowledge
- each role folder has `_shared-links` symlinks to avoid duplicating shared sources
- each role folder contains structured ingestion-ready metadata templates

### 3. Universal Agent Skills

The repository includes a portable `skills/` ecosystem using `SKILL.md`-style packaging compatible with:

- Claude
- Codex
- OpenClaw
- Hermes Agent
- Antigravity

There are:

- **29 role skills**
- **1 shared guardrail skill**
- a machine-readable `skills/skill_manifest.json`
- generator and validator scripts for deterministic skill management

### 4. Governance, Safety, and Auditability

The repository includes contracts and templates for:

- action-level control (`L0` to `L4`)
- data classification handling
- audit logging
- role conflict handling
- human review and approval
- acceptance tests and validation prompts

## Production Adoption Model

This repository is intended to be used as a **baseline implementation kit**.

A production adopter is expected to:

1. preserve the repo contracts
2. replace example or starter content with agency-specific sources
3. populate the knowledge base with official documents
4. connect a real retrieval and audit layer
5. enforce data classification and HITL rules in runtime
6. validate behavior with the provided test suite

This repo is therefore both:

- a **reference architecture**, and
- a **working starter system** for real implementation.

## Architecture Map

### Core Layers

- **Orchestration Layer**
  - Yayak routes requests, classifies intent, determines action level, detects risk, and preserves `trace_id`.
- **Role Execution Layer**
  - specialist skills handle domain-specific drafting, review, analysis, and challenge functions.
- **Knowledge Layer**
  - role knowledge and shared knowledge support grounded outputs and reusable retrieval.
- **Governance Layer**
  - HITL, audit, compliance, and escalation policies ensure the system behaves within public-sector boundaries.
- **Validation Layer**
  - acceptance tests, repo verification, and skill verification ensure portability and consistency.

### Minimum Production Components

A real deployment based on this repo should provide:

- identity and access control
- orchestration runtime
- retrieval layer over knowledge-base content
- audit log storage
- human approval interface or workflow
- observability for routing, evidence, and escalation events

## Agent Role Ecosystem Summary

The current role inventory is tracked in:

- `knowledge-base/kb_manifest.json`
- `skills/skill_manifest.json`

Current inventory:

- **29 roles**
- **10 clusters**
- **1 shared guardrail skill**

Role patterns:

- **Orchestrator**: Yayak
- **Specialist Roles**: domain drafting, analysis, and workflow execution
- **Monitor / Compliance Roles**: challenge, evidence review, audit readiness, block/hold recommendations
- **Escalation Role**: Winda for unresolved conflicts and human takeover paths

## Knowledge Base Structure

The knowledge layer is designed for long-term operational use, not just demo retrieval.

### Shared Knowledge

`knowledge-base/_shared`

Use this for knowledge reused by many roles, such as:

- general regulations
- global SOPs
- organization-wide templates
- data dictionaries
- audit and compliance references
- golden output examples

### Role Knowledge

`knowledge-base/<cluster>/<role>`

Use this for:

- role-specific source documents
- role-specific examples
- role-specific reference data
- role-specific review notes
- ingestion-ready curated files

### Standard Subdirectories Per Role

Each role folder follows the same structure:

- `00-readme`
- `01-source-documents`
- `02-regulations-and-policies`
- `03-templates-and-examples`
- `04-sop-and-workflows`
- `05-reference-data`
- `06-output-samples`
- `07-review-notes`
- `08-ingestion-ready`
- `09-archive`

## Skill Ecosystem Structure

The skill layer is designed as a **portable agent capability package** rather than a runtime-specific hack.

### Layout

- `skills/roles/` contains the 29 role skills
- `skills/_shared/gov-agentic-common/` contains shared guardrails
- `skills/skill_manifest.json` contains the machine-readable skill registry
- `scripts/generate_role_skills.py` generates deterministic role skills
- `scripts/verify_skills.py` validates skill integrity

### Skill Contract

Each role skill includes:

- `SKILL.md`
- `references/role-profile.md`
- `references/output-contract.md`
- `references/knowledge-map.md`
- `assets/.gitkeep`
- `scripts/.gitkeep`

Each skill is intentionally lightweight and references:

- the role prompt under `prompts/roles/`
- the role knowledge folder under `knowledge-base/`
- the shared guardrail skill under `skills/_shared/`

## Governance, HITL, Audit, and Data Classification

This repository assumes that **governance is part of the system**, not a separate policy document nobody uses.

### Human-in-the-Loop

HITL is required for:

- `L3` formal artifact preparation
- `L4` external or impactful execution
- sensitive data
- low-confidence evidence
- unresolved cross-role conflict
- legal, fiscal, procurement, or public-impact situations

### Audit Contract

The canonical audit schema lives in:

- `schemas/audit_log_template_v3.0.json`

This is the minimum contract for:

- traceability
- role chain logging
- conflict logging
- human approval state
- artifact versioning
- final status capture

### Data Classification

The repository assumes at least four classes:

- `public`
- `internal`
- `restricted`
- `sensitive`

Handling expectations are documented in:

- `docs/security/DATA_CLASSIFICATION_AND_HANDLING.md`

## 30/60/90-Day Pilot Roadmap

### Day 0-30: Foundation

- appoint sponsor, product owner, data owners, reviewers
- choose the initial workflow subset
- stand up the knowledge and audit foundations
- ingest initial official sources
- validate repo, skill, and contract integrity

### Day 31-60: Controlled Pilot

- run with limited users and strict HITL
- measure routing accuracy, evidence quality, and review burden
- exercise red-team and prompt-injection scenarios
- refine prompts, knowledge, and escalation rules

### Day 61-90: Limited Production Decision

- expand only if governance and incident review support it
- validate operational readiness across workflow, risk, and audit dimensions
- decide: continue, hold, redesign, or scale

## Install from Terminal

This repository is currently private, so raw GitHub URLs return `404` unless authenticated. Use GitHub CLI (`gh`) for the private-repo install path. See [`INSTALL.md`](./INSTALL.md).

macOS / Linux:

```bash
gh repo clone dendyadinirwana/gov-agentic-AI && cd gov-agentic-AI && ./install.sh --target-dir .
```

Windows PowerShell:

```powershell
gh repo clone dendyadinirwana/gov-agentic-AI; cd gov-agentic-AI; ./install.ps1 -TargetDir .
```

## Quick Start for Adopters

### 1. Review the implementation baseline

Start with:

- `docs/governance/Gov_Agentic_AI_v3.1_Implementation_Pack.md`
- `docs/operations/REPLICATION_GUIDE.md`
- `docs/operations/SKILL_ADOPTION_GUIDE.md`

### 2. Review the repository contract

Critical files:

- `knowledge-base/kb_manifest.json` — role inventory
- `skills/skill_manifest.json` — skill inventory
- `schemas/audit_log_template_v3.0.json` — audit contract
- `prompts/system/YayakAI_Master_System_Prompt_v3.0.md` — orchestration prompt

### 3. Populate knowledge

Populate:

- `knowledge-base/_shared`
- role-specific folders under `knowledge-base/<cluster>/<role>`

### 4. Connect runtime behavior

Wire the runtime to:

- system prompt
- role prompts
- role skills
- role knowledge
- audit log schema
- human approval flow

### 5. Validate before adoption

Run:

```bash
python3 scripts/verify_repo.py
python3 scripts/verify_skills.py
python3 scripts/generate_role_skills.py --check
```

## Validation Commands

Use these commands as the minimum repository health check:

```bash
python3 scripts/verify_repo.py
python3 scripts/verify_skills.py
python3 scripts/generate_role_skills.py --check
```

Expected outcomes:

- repo contracts present
- no broken symlinks
- role count and skill count aligned
- skill frontmatter valid
- prompt and knowledge paths intact

## Repository Map

- `docs/` — architecture, governance, operations, security, knowledge-model references
- `prompts/` — orchestration and role prompts
- `schemas/` — audit and acceptance-test schemas
- `knowledge-base/` — role and shared knowledge layout
- `skills/` — universal role skills and shared guardrails
- `operations/` — bootstrap, ingestion, and review templates
- `examples/` — sample requests and output contracts
- `configs/` — deployment template
- `scripts/` — generators and validators

## Document Deliverables

Root DOCX artifacts remain available as downloadable deliverables:

- [`Gov_Agentic_AI_v3.1_Implementation_Pack.docx`](./Gov_Agentic_AI_v3.1_Implementation_Pack.docx)
- [`Gov_Agentic_AI_v3.0_Master_Full.docx`](./Gov_Agentic_AI_v3.0_Master_Full.docx)
- [`Gov_Agentic_AI_v3.0_Knowledge_UseCases.docx`](./Gov_Agentic_AI_v3.0_Knowledge_UseCases.docx)

Additional canonical Markdown references:

- [`docs/governance/Gov_Agentic_AI_v3.1_Implementation_Pack.md`](./docs/governance/Gov_Agentic_AI_v3.1_Implementation_Pack.md)
- [`docs/operations/Gov_Agentic_AI_Cross_Cluster_Playbook_v3.0.md`](./docs/operations/Gov_Agentic_AI_Cross_Cluster_Playbook_v3.0.md)
- [`docs/architecture/Gov_Agentic_AI_Persona_Alias_Annex_v3.0.md`](./docs/architecture/Gov_Agentic_AI_Persona_Alias_Annex_v3.0.md)

## Why This Repo Matters

Most AI repository examples stop at prompts, demo agents, or toy retrieval. This repository is aimed at a harder target:

- production adoption
- role accountability
- auditable behavior
- reusable knowledge structure
- cross-runtime skill portability
- human-governed execution in public-sector contexts

That is the reason this repository exists.
