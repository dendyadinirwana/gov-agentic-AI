#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIMES = ('openclaw', 'hermes', 'codex', 'claude', 'antigravity', 'generic')


def runtime_target_root(runtime: str) -> Path:
    mapping = {
        'openclaw': Path.home() / '.openclaw' / 'gov-agentic-ai',
        'hermes': Path.home() / '.hermes' / 'gov-agentic-ai',
        'codex': Path.home() / '.codex' / 'gov-agentic-ai',
        'claude': Path.home() / '.claude' / 'gov-agentic-ai',
        'antigravity': Path.home() / '.antigravity' / 'gov-agentic-ai',
        'generic': Path.home() / '.agents' / 'skills' / 'gov-agentic-ai',
    }
    return mapping[runtime]


def run_check(label: str, cmd: list[str]) -> int:
    print(f'--- {label} ---')
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description='Run Gov-Agentic AI installation diagnostics.')
    parser.add_argument('--runtime', choices=RUNTIMES, default='generic', help='Runtime shim to inspect.')
    parser.add_argument('--shim-root', help='Explicit runtime shim root override.')
    parser.add_argument('--config', default='configs/runtime.generated.json', help='Runtime config path to validate.')
    parser.add_argument('--skip-repo', action='store_true', help='Skip repo structure verification.')
    parser.add_argument('--skip-skills', action='store_true', help='Skip skill verification.')
    parser.add_argument('--skip-config', action='store_true', help='Skip runtime config verification.')
    parser.add_argument('--skip-attach', action='store_true', help='Skip runtime attach verification.')
    args = parser.parse_args()

    checks: list[tuple[str, list[str]]] = []
    config_path = Path(args.config)
    shim_root = Path(args.shim_root).expanduser() if args.shim_root else runtime_target_root(args.runtime)

    if not args.skip_repo:
        checks.append(('Repo Verification', [sys.executable, 'scripts/verify_repo.py']))
    if not args.skip_skills:
        checks.append(('Skill Verification', [sys.executable, 'scripts/verify_skills.py']))
    if not args.skip_config:
        checks.append(('Runtime Config Verification', [sys.executable, 'scripts/verify_runtime_config.py', str(config_path)]))
    if not args.skip_attach:
        checks.append(('Runtime Attach Verification', [sys.executable, 'scripts/verify_runtime_attach.py', str(shim_root)]))

    failures = 0
    print('Gov-Agentic AI doctor')
    print(f'repo_root={ROOT}')
    print(f'runtime={args.runtime}')
    print(f'shim_root={shim_root}')
    print(f'config={config_path}')
    for label, cmd in checks:
        code = run_check(label, cmd)
        if code != 0:
            failures += 1
            print(f'status={label}:failed:{code}')
        else:
            print(f'status={label}:ok')

    print(f'checks={len(checks)}')
    print(f'failures={failures}')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
