#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = [
    'runtime.generated.json',
    'active.deployment.yaml',
    'runtime-adapter.profile.json',
    'active-skills.json',
    'runtime-pack.manifest.json',
]


def main() -> int:
    pack_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('build/runtime-pack')
    if not pack_root.exists():
        print(f'ERROR: missing pack root: {pack_root}')
        return 1
    candidate = pack_root
    if pack_root.is_dir() and not (pack_root / 'runtime.generated.json').exists():
        manifests = sorted(pack_root.rglob('runtime.generated.json'))
        if not manifests:
            print(f'ERROR: no runtime.generated.json found under {pack_root}')
            return 1
        candidate = manifests[-1].parent
    errors: list[str] = []
    for rel in REQUIRED:
        if not (candidate / rel).exists():
            errors.append(f'missing pack file: {rel}')
    if not errors:
        config = json.loads((candidate / 'runtime.generated.json').read_text())
        manifest = json.loads((candidate / 'runtime-pack.manifest.json').read_text())
        skill_manifest = json.loads((candidate / 'active-skills.json').read_text())
        if manifest.get('runtime_target') != config.get('runtime_target'):
            errors.append('manifest runtime_target does not match runtime config')
        if len(skill_manifest.get('skills', [])) != len(config.get('active_skills', [])):
            errors.append('active-skills.json does not match active_skills count')
    print(f'pack_root={candidate}')
    print(f'errors={len(errors)}')
    for error in errors:
        print(f'ERROR: {error}')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
