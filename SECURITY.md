# Security Policy

## Scope

This repository contains architecture, prompts, knowledge-base structure, schemas, and operational guidance for a government-grade agentic AI baseline.

## Security Expectations

Contributors must preserve:

- Human-in-the-Loop requirements for L3/L4 actions
- audit log completeness
- data-classification boundaries
- escalation paths for legal, fiscal, procurement, or sensitive cases
- role-based separation of responsibilities

## Reporting a Security Concern

If you discover a security issue in this repository design or implementation guidance, do not open a public issue with sensitive exploit detail.

Instead, report privately to the repository owner and include:

- affected file or contract
- risk summary
- likely impact
- reproduction path or misuse scenario
- suggested mitigation

## Examples of Security-Relevant Issues

- prompt instructions that weaken approval or audit gates
- schemas that allow silent loss of review metadata
- role skills that bypass escalation rules
- repository guidance that could leak sensitive government information
- knowledge-base layout changes that break data-separation assumptions
