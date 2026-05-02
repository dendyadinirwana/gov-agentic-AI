# Runtime Handshake

This document defines the minimum handshake a compatible runtime should complete before treating this repository as an active Gov-Agentic AI deployment.

## Handshake Goal
A runtime must prove that it can:

- resolve the agent entrypoint
- load the runtime config
- identify active roles and active skills
- initialize the government decision engine
- enforce governance and HITL rules
- fail closed if bootstrap is incomplete

## Required Read Order
1. `AGENT_README.md`
2. `configs/runtime.generated.json`
3. `runtime-adapters/<runtime>/profile.json` or `runtime-adapters/universal/AGENT_RUNTIME.md`
4. `prompts/system/YayakAI_Master_System_Prompt_v3.0.md`
5. `skills/_shared/gov-agentic-common/SKILL.md`
6. decision engine dependencies declared in runtime config

## Minimum Handshake Assertions
A runtime should not continue unless all of these are true:

- `agent_entrypoint` resolves to `AGENT_README.md`
- `runtime_target` is known
- `default_router_alias` resolves to `Yayak`
- `active_roles` is non-empty
- `active_skills` is non-empty
- `decision_engine.enabled` is true unless explicitly disabled by policy
- `governance_mode` is present
- `human_approval_required_for` is present

## Fail-Closed Rule
If any required bootstrap input is missing or inconsistent, stop initialization and return a bootstrap error. Do not degrade into a generic assistant mode.

## Install-Aware Runtime Behavior
If installed under a managed runtime home, the runtime should also read:

- `install.receipt.json`
- `runtime-pack.manifest.json`

Use them to confirm install target, source commit version, managed subtree, and pack integrity.
