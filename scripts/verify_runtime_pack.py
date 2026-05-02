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
    'AGENT_README.md',
    'runtime-adapters/universal/AGENT_RUNTIME.md',
    'runtime-adapters/universal/RUNTIME_HANDSHAKE.md',
    'examples/BOOTSTRAP_EXAMPLE.json',
]

def locate_candidate(pack_root: Path) -> Path:
    if pack_root.is_dir() and (pack_root / 'runtime.generated.json').exists():
        return pack_root
    manifests = sorted(pack_root.rglob('runtime.generated.json'), key=lambda p: p.stat().st_mtime)
    if not manifests:
        raise FileNotFoundError(f'no runtime.generated.json found under {pack_root}')
    return manifests[-1].parent

def main() -> int:
    pack_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('build/runtime-pack')
    if not pack_root.exists():
        print(f'ERROR: missing pack root: {pack_root}')
        return 1
    try:
        candidate = locate_candidate(pack_root)
    except FileNotFoundError as exc:
        print(f'ERROR: {exc}')
        return 1

    errors: list[str] = []
    for rel in REQUIRED:
        if not (candidate / rel).exists():
            errors.append(f'missing pack file: {rel}')

    if not errors:
        config = json.loads((candidate / 'runtime.generated.json').read_text())
        manifest = json.loads((candidate / 'runtime-pack.manifest.json').read_text())
        skills = json.loads((candidate / 'active-skills.json').read_text())
        if manifest.get('runtime_target') != config.get('runtime_target'):
            errors.append('manifest runtime_target does not match runtime config')
        if manifest.get('agent_entrypoint') != config.get('agent_entrypoint'):
            errors.append('manifest agent_entrypoint does not match runtime config')
        if len(skills.get('skills', [])) != len(config.get('active_skills', [])):
            errors.append('active-skills.json does not match active_skills count')
        if manifest.get('bootstrap_example') != 'examples/BOOTSTRAP_EXAMPLE.json':
            errors.append('manifest bootstrap_example must point to examples/BOOTSTRAP_EXAMPLE.json')
        checksums = manifest.get('checksums')
        if not isinstance(checksums, dict) or not checksums:
            errors.append('runtime-pack.manifest.json must contain non-empty checksums')
        else:
            for rel, digest in checksums.items():
                if not (candidate / rel).exists():
                    errors.append(f'checksum entry points to missing file: {rel}')
                if not isinstance(digest, str) or len(digest) < 32:
                    errors.append(f'invalid checksum for: {rel}')

    print(f'pack_root={candidate}')
    print(f'errors={len(errors)}')
    for error in errors:
        print(f'ERROR: {error}')
    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
