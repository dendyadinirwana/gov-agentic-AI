#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNTIMES = ('openclaw', 'hermes', 'codex', 'claude', 'antigravity', 'generic')
MANAGED_SUBTREE = 'gov-agentic-ai'
CENTRAL_HOME = Path.home() / '.gov-agentic-ai'


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def runtime_profile(runtime: str) -> dict[str, Any]:
    profile_path = ROOT / 'runtime-adapters' / runtime / 'profile.json'
    if not profile_path.exists():
        raise FileNotFoundError(f'missing runtime profile: {profile_path}')
    return load_json(profile_path)


def resolve_target_root(runtime: str, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    profile = runtime_profile(runtime)
    target = profile.get('install_target_root')
    if not isinstance(target, str) or not target:
        raise ValueError(f'install_target_root missing for runtime: {runtime}')
    return Path(target).expanduser().resolve()


def is_safe_managed_root(target_root: Path) -> tuple[bool, str]:
    if target_root.name != MANAGED_SUBTREE:
        return False, f'target root must end with {MANAGED_SUBTREE}'
    if len(target_root.parts) < 3:
        return False, 'target root is unexpectedly shallow'
    receipt = target_root / 'install.receipt.json'
    runtime_config = target_root / 'runtime.generated.json'
    if not receipt.exists() and not runtime_config.exists():
        return False, 'target root does not look like a managed Gov-Agentic AI install'
    return True, 'ok'


def preview(target_root: Path) -> dict[str, Any]:
    exists = target_root.exists()
    files = [p for p in target_root.rglob('*')] if exists else []
    file_count = sum(1 for p in files if p.is_file())
    sample = []
    if exists:
        for path in sorted(files)[:12]:
            rel = path.relative_to(target_root)
            sample.append(f"{'[D]' if path.is_dir() else '[F]'} {rel}")
    return {
        'exists': exists,
        'file_count': file_count,
        'sample': sample or ['(target missing)'],
    }


def maybe_remove_repo_generated(remove_local_generated: bool) -> list[str]:
    removed: list[str] = []
    if not remove_local_generated:
        return removed
    for rel in ['configs/runtime.generated.json', 'configs/active.deployment.yaml']:
        path = ROOT / rel
        if path.exists():
            path.unlink()
            removed.append(rel)
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description='Safely uninstall Gov-Agentic AI runtime shims or the canonical central home.')
    parser.add_argument('--runtime', choices=RUNTIMES, default='generic', help='Runtime target to uninstall from.')
    parser.add_argument('--target-root', help='Explicit managed install root to remove.')
    parser.add_argument('--dry-run', action='store_true', help='Preview removal without deleting anything.')
    parser.add_argument('--remove-local-generated', action='store_true', help='Also remove repo-local generated config files under configs/.')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation prompt.')
    parser.add_argument('--remove-central-home', action='store_true', help='Also remove ~/.gov-agentic-ai canonical home.')
    args = parser.parse_args()

    target_root = resolve_target_root(args.runtime, args.target_root)
    safe, message = is_safe_managed_root(target_root)
    if not safe:
        print(f'ERROR: {message}')
        print(f'target_root={target_root}')
        return 1

    info = preview(target_root)
    print(f'runtime={args.runtime}')
    print(f'target_root={target_root}')
    print(f'exists={info["exists"]}')
    print(f'file_count={info["file_count"]}')
    for line in info['sample']:
        print(f'preview={line}')

    if args.dry_run:
        print('dry_run=True')
        return 0

    if not args.yes:
        response = input('Type uninstall to confirm removal: ').strip()
        if response != 'uninstall':
            print('Cancelled.')
            return 1

    shutil.rmtree(target_root)
    removed_local = maybe_remove_repo_generated(args.remove_local_generated)
    print(f'removed_target_root={target_root}')
    if args.remove_central_home and CENTRAL_HOME.exists():
        shutil.rmtree(CENTRAL_HOME)
        print(f'removed_central_home={CENTRAL_HOME}')
    if removed_local:
        print(f'removed_repo_generated={",".join(removed_local)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
