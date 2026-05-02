# Hermes Adapter

## Goal
Use this repository as a persistent agent identity and governance package for Hermes.

## Required Policy
- Hermes must treat local knowledge as canonical when `memory_mode=local` or `memory_mode=hybrid`.
- Hermes may store session memory and preferences in mem9 under `hybrid`.
- Hermes must not overwrite canonical repo knowledge from mem9 recall.
- Hermes must preserve audit and HITL rules from the generated runtime config.

## Recommended Boot
1. Read `configs/runtime.generated.json`.
2. Load Yayak system identity.
3. Load shared guardrail skill.
4. Restrict role routing to `active_roles`.
5. Persist working memory according to `memory_mode`.
