# Contributing

Thank you for contributing to **Gov-Agentic AI**.

This repository is a production-oriented baseline for government-grade agentic AI. Contributions should preserve its core contracts: governance, auditability, Human-in-the-Loop controls, role inventory, and portable skills.

## Contribution Principles

- Preserve repository contracts documented in `docs/architecture/REPO_CONTRACT.md`.
- Prefer shared knowledge and symlinks over duplicating the same source into many role folders.
- Do not remove audit fields or role inventory entries casually.
- Keep prompts, skills, manifests, and knowledge-base paths aligned.
- Do not weaken HITL, data-classification, or escalation requirements.

## Before You Commit

Run:

```bash
python3 scripts/verify_repo.py
python3 scripts/smoke_test_agent_to_agent.py
python3 scripts/smoke_test_agent_to_agent_matrix.py
python3 -m unittest discover -s tests -v
```

Expected:

- no broken symlinks
- core orchestration fixtures remain valid
- contract validation stays green
- retrieval and HITL flows remain covered by tests
- required manifests and contracts remain present

## Change Categories

### Safe changes

- add or improve shared documentation
- enrich role knowledge folders
- improve examples and output templates
- improve skill wording without breaking paths or contracts
- add adoption and operations guides

### High-sensitivity changes

These need extra care and explicit review:

- role renames
- manifest schema changes
- audit schema changes
- prompt contract changes
- HITL logic changes
- data-classification handling changes
- symlink/layout changes inside `knowledge-base/`

## Pull Request Guidance

A good contribution should explain:

- what changed
- why it changed
- whether repo contracts or runtime assumptions changed
- how it was validated
- what still needs runtime or human verification

## Knowledge Base Editing Rule

If a document will be reused by 3 or more roles, prefer placing it under `knowledge-base/_shared` and linking it from role folders.
