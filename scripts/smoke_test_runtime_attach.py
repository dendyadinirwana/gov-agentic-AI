#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIMES = ('hermes', 'openclaw', 'generic')


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)


def count_files(path: Path) -> int:
    return sum(1 for p in path.rglob('*') if p.is_file()) if path.exists() else 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Smoke test central-home + thin-shim runtime attachment.')
    parser.add_argument('--runtime', choices=RUNTIMES, required=True)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix=f'gov-agentic-{args.runtime}-') as tmp:
        tmp_root = Path(tmp)
        runtime_home = tmp_root / args.runtime / 'gov-agentic-ai'
        central_home = tmp_root / '.gov-agentic-ai'
        output = ROOT / 'configs' / f'runtime.{args.runtime}.smoke.json'
        active = ROOT / 'configs' / f'active.{args.runtime}.smoke.yaml'
        cmd = [
            sys.executable,
            'scripts/install_gov_agentic_ai.py',
            '--defaults',
            '--runtime',
            args.runtime,
            '--install-target-root',
            str(runtime_home),
            '--central-home-root',
            str(central_home),
            '--output',
            str(output),
            '--active-deployment',
            str(active),
        ]
        result = run(cmd)
        config = json.loads(output.read_text())
        shim_link = json.loads((runtime_home / 'runtime-link.json').read_text())
        yayak = runtime_home / 'skills' / 'roles' / 'top-layer__gov-ai_yayak' / 'SKILL.md'
        central_manifest = central_home / 'skills' / 'skill_manifest.json'

        errors: list[str] = []
        if config.get('central_home_root') != str(central_home):
            errors.append('runtime config central_home_root mismatch')
        if shim_link.get('central_home_root') != str(central_home):
            errors.append('runtime-link central_home_root mismatch')
        if not yayak.exists():
            errors.append('local Yayak skill missing in shim')
        if not central_manifest.exists():
            errors.append('central skill manifest missing')
        if count_files(runtime_home) >= 200:
            errors.append('runtime shim is too large; thin shim expectation violated')
        if count_files(central_home) <= count_files(runtime_home):
            errors.append('central home should be larger than runtime shim')

        print(f'runtime={args.runtime}')
        print(f'central_home={central_home}')
        print(f'runtime_home={runtime_home}')
        print(f'runtime_shim_files={count_files(runtime_home)}')
        print(f'central_home_files={count_files(central_home)}')
        print(f'errors={len(errors)}')
        for error in errors:
            print(f'ERROR: {error}')

        for path in [output, active]:
            if path.exists():
                path.unlink()
        return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
