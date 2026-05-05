#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

RUNTIME_REQUIRED = [
    'runtime.generated.json',
    'runtime-bootstrap.generated.json',
    'active.deployment.yaml',
    'runtime-adapter.profile.json',
    'active-skills.json',
    'runtime-pack.manifest.json',
    'runtime-link.json',
    'AGENT_README.md',
    'runtime-adapters/universal/AGENT_RUNTIME.md',
    'runtime-adapters/universal/RUNTIME_HANDSHAKE.md',
    'examples/BOOTSTRAP_EXAMPLE.json',
    'skills/roles/top-layer__gov-ai_yayak/SKILL.md',
]
CENTRAL_REQUIRED = [
    'configs/runtime.generated.json',
    'configs/runtime-bootstrap.generated.json',
    'configs/role_registry.json',
    'central-home.manifest.json',
    'skills/skill_manifest.json',
    'knowledge-base/kb_manifest.json',
    'AGENT_README.md',
]

def locate_candidate(pack_root: Path, manifest_name: str) -> Path:
    if pack_root.is_dir() and (pack_root / manifest_name).exists():
        return pack_root
    manifests = sorted(pack_root.rglob(manifest_name), key=lambda p: p.stat().st_mtime)
    if not manifests:
        raise FileNotFoundError(f'no {manifest_name} found under {pack_root}')
    return manifests[-1].parent

def validate_checksums(candidate: Path, manifest: dict, errors: list[str]) -> None:
    checksums = manifest.get('checksums')
    if not isinstance(checksums, dict) or not checksums:
        errors.append('manifest must contain non-empty checksums')
        return
    for rel, digest in checksums.items():
        if not (candidate / rel).exists():
            errors.append(f'checksum entry points to missing file: {rel}')
        if not isinstance(digest, str) or len(digest) < 32:
            errors.append(f'invalid checksum for: {rel}')

def main() -> int:
    pack_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('build/runtime-pack')
    pack_kind = sys.argv[2] if len(sys.argv) > 2 else 'runtime'
    if not pack_root.exists():
        print(f'ERROR: missing pack root: {pack_root}')
        return 1
    manifest_name = 'central-home.manifest.json' if pack_kind == 'central' else 'runtime-pack.manifest.json'
    required = CENTRAL_REQUIRED if pack_kind == 'central' else RUNTIME_REQUIRED
    try:
        candidate = locate_candidate(pack_root, manifest_name)
    except FileNotFoundError as exc:
        print(f'ERROR: {exc}')
        return 1
    errors: list[str] = []
    for rel in required:
        if not (candidate / rel).exists():
            errors.append(f'missing pack file: {rel}')
    if not errors:
        manifest = json.loads((candidate / manifest_name).read_text())
        validate_checksums(candidate, manifest, errors)
        if pack_kind == 'runtime':
            config = json.loads((candidate / 'runtime.generated.json').read_text())
            link = json.loads((candidate / 'runtime-link.json').read_text())
            if manifest.get('pack_kind') != 'runtime-shim':
                errors.append('runtime pack manifest must have pack_kind=runtime-shim')
            if link.get('runtime_attach_mode') != 'thin-shim':
                errors.append('runtime-link.json must declare thin-shim attach mode')
            if 'gov-gov-ai-yayak' not in link.get('shim_installed_skills', []):
                errors.append('runtime-link.json must include gov-gov-ai-yayak in shim_installed_skills')
            if config.get('central_home_root') != link.get('central_home_root'):
                errors.append('runtime.generated.json central_home_root must match runtime-link.json')
        else:
            config = json.loads((candidate / 'configs' / 'runtime.generated.json').read_text())
            if manifest.get('pack_kind') != 'central-home':
                errors.append('central pack manifest must have pack_kind=central-home')
            if config.get('runtime_attach_mode') != 'thin-shim':
                errors.append('central runtime config must keep thin-shim attach mode')
    print(f'pack_root={candidate}')
    print(f'pack_kind={pack_kind}')
    print(f'errors={len(errors)}')
    for error in errors:
        print(f'ERROR: {error}')
    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
