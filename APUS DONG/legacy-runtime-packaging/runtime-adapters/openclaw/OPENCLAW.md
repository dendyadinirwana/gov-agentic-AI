# OpenClaw Adapter

## Goal
Mount this repository into OpenClaw and point the runtime to `configs/runtime.generated.json` or local shim `openclaw.runtime.config.json`.

## Expected Loading Order
1. Load runtime config.
2. Load system prompt.
3. Load shared guardrail skill.
4. Load only active role skills.
5. Route requests through Yayak unless a role is explicitly preselected.

## Memory Notes
- `local`: use repository knowledge only
- `mem9`: use mem9 as primary memory surface
- `hybrid`: local repo remains canonical; mem9 stores preferences/session memory

## Decision Engine Hook
- Load the configured decision engine before role routing.
- Run it on each incoming request to determine state, authority, and gate decision.
- Respect `HOLD` and `ESCALATE_TO` as hard control outputs in production deployments.
