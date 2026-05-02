# Runtime Adapters

Runtime adapters tell an agent runtime how to recognize this repository as Gov-Agentic AI.

The canonical runtime entrypoint is:

```text
configs/runtime.generated.json
```

## Generic vs Specific Runtime

- `generic` is the global fallback for any runtime that can read repository files and JSON config.
- Specific profiles add runtime-aware path hints for OpenClaw, Hermes, Codex, Claude, and Antigravity.
- The installer always keeps repo-local config canonical and records external runtime locations as advisory targets.

## Adapter Profiles

Each runtime can define `runtime-adapters/<runtime>/profile.json` with:

- `adapter_name`
- `adapter_path`
- `folder_strategy`
- `skill_loading`
- `config_entrypoint`
- `runtime_paths`
- `runtime_overrides`

The installer merges the selected profile into `configs/runtime.generated.json` under:

- `runtime_adapter`
- `adapter_name`
- `adapter_profile_path`
- `runtime_paths`
- `runtime_overrides`

## Runtime Discovery

Installer v3 scans common OS-specific runtime homes and writes the result to:

- `runtime_discovery`
- `runtime_installation`
- `runtime_config_targets`

Discovery is advisory by default. The installer does not mutate Hermes, OpenClaw, Codex, Claude, or Antigravity config folders unless a future explicit write mode is added.

## Memory Precedence

In `hybrid`, local repo knowledge remains the canonical source of truth. mem9 can store preferences, session memory, and operational recall, but must not overwrite canonical knowledge from this repository.


## Install Contract

Each adapter profile now acts as an install contract and should define canonical home roots, managed install subtree, config target, and skill target expectations. The installer uses those semantics to generate a runtime pack and install it by copy into the managed `gov-agentic-ai` subtree.

## Bootstrap Contract
Universal bootstrap guidance lives in `runtime-adapters/universal/RUNTIME_HANDSHAKE.md`, with a machine-readable example at `examples/BOOTSTRAP_EXAMPLE.json`. Runtime-specific adapters should refine filesystem and install behavior, not redefine the bootstrap contract.
