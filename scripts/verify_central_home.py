#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = [
    'AGENT_README.md',
    'configs/runtime.generated.json',
    'central-home.manifest.json',
    'knowledge-base/kb_manifest.json',
    'skills/skill_manifest.json',
    'prompts/system/YayakAI_Master_System_Prompt_v3.0.md',
]

def main() -> int:
    root = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.home() / '.gov-agentic-ai'
    errors = []
    if not root.exists():
        print(f'ERROR: missing central home: {root}')
        return 1
    for rel in REQUIRED:
        if not (root / rel).exists():
            errors.append(f'missing central home file: {rel}')
    if not errors:
        config = json.loads((root / 'configs/runtime.generated.json').read_text())
        if config.get('central_home_root') != str(root):
            errors.append('central runtime config must point back to installed central home root')
    print(f'central_home_root={root}')
    print(f'errors={len(errors)}')
    for error in errors:
        print(f'ERROR: {error}')
    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
