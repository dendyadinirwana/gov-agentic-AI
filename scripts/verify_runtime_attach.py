#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_SHIM_FILES = [
    'runtime.generated.json',
    'runtime-bootstrap.generated.json',
    'runtime-link.json',
    'skills/roles/top-layer__gov-ai_yayak/SKILL.md',
    'AGENT_README.md',
]
ADAPTER_EXPORTS = {
    'hermes': ['hermes.runtime.config.yaml'],
    'openclaw': ['openclaw.runtime.config.json'],
}

REQUIRED_CENTRAL_FILES = [
    'configs/runtime.generated.json',
    'configs/runtime-bootstrap.generated.json',
    'configs/role_registry.json',
    'skills/skill_manifest.json',
    'knowledge-base/kb_manifest.json',
    'prompts/system/YayakAI_Master_System_Prompt_v3.0.md',
]

def load_json(path: Path) -> dict:
    return json.loads(path.read_text())

def main() -> int:
    shim_root = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.home() / '.agents' / 'skills' / 'gov-agentic-ai'
    errors: list[str] = []
    if not shim_root.exists():
        print(f'ERROR: missing runtime shim root: {shim_root}')
        return 1
    for rel in REQUIRED_SHIM_FILES:
        if not (shim_root / rel).exists():
            errors.append(f'missing shim file: {rel}')
    if not errors:
        config = load_json(shim_root / 'runtime.generated.json')
        bootstrap = load_json(shim_root / 'runtime-bootstrap.generated.json')
        link = load_json(shim_root / 'runtime-link.json')
        central_root = Path(link['central_home_root']).expanduser()
        for rel in REQUIRED_CENTRAL_FILES:
            if not (central_root / rel).exists():
                errors.append(f'missing central file: {rel}')
        if bootstrap.get('default_router_skill') != 'gov-gov-ai-yayak':
            errors.append('bootstrap default_router_skill must be gov-gov-ai-yayak')
        if bootstrap.get('runtime_attach_mode') != 'thin-shim':
            errors.append('bootstrap runtime_attach_mode must be thin-shim')
        if link.get('canonical_runtime_config') != config.get('canonical_runtime_config'):
            errors.append('runtime-link canonical_runtime_config must match runtime.generated.json')
        if bootstrap.get('path_registry', {}).get('canonical_skill_manifest') != config.get('canonical_skill_manifest'):
            errors.append('bootstrap path_registry canonical_skill_manifest must match runtime.generated.json')
        for rel in ADAPTER_EXPORTS.get(config.get('runtime_target'), []):
            if not (shim_root / rel).exists():
                errors.append(f'missing runtime-native export: {rel}')
    print(f'shim_root={shim_root}')
    if not errors:
        print(f'central_home_root={link.get("central_home_root")}')
        print(f'runtime_target={config.get("runtime_target")}')
        print(f'default_router_alias={bootstrap.get("default_router_alias")}')
        print(f'bootstrap_scope={bootstrap.get("bootstrap_scope")}')
    print(f'errors={len(errors)}')
    for error in errors:
        print(f'ERROR: {error}')
    return 1 if errors else 0

if __name__ == '__main__':
    raise SystemExit(main())
