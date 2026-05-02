# Runtime Adapters

Runtime adapters tell an agent runtime how to recognize this repository as Gov-Agentic AI.

## Profiles

Each runtime can define a `profile.json` with:

- `adapter_name`
- `adapter_path`
- `folder_strategy`
- `skill_loading`
- `config_entrypoint`
- `runtime_paths`
- `runtime_overrides`

The installer merges the selected profile into `configs/runtime.generated.json`.

## Generic vs Specific Runtime

- `generic` is the global fallback for any runtime that can read repository files.
- runtime-specific profiles add path and behavior hints for OpenClaw, Hermes, Codex, Claude, and Antigravity.

## Memory Precedence

In `hybrid`, local repo knowledge remains the canonical source of truth. mem9 can store preferences, session memory, and operational recall, but must not overwrite canonical knowledge.
