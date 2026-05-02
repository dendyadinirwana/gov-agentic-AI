#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / 'knowledge-base'


def main() -> int:
    if len(sys.argv) != 2:
        print('usage: python3 scripts/scaffold_ingestion_bundle.py <cluster/role_path>')
        return 2
    role_path = sys.argv[1].strip().strip('/')
    ingest_dir = KB / role_path / '08-ingestion-ready'
    if not ingest_dir.exists():
        print(f'missing role ingestion dir: {ingest_dir}')
        return 1
    manifest_template = ingest_dir / 'bundle.manifest.template.json'
    manifest_target = ingest_dir / 'bundle.manifest.json'
    if not manifest_target.exists():
        shutil.copyfile(manifest_template, manifest_target)
        print(f'created {manifest_target.relative_to(ROOT)}')
    else:
        print(f'exists {manifest_target.relative_to(ROOT)}')
    for folder in ['raw','clean','published']:
        (ingest_dir / folder).mkdir(exist_ok=True)
    example = ingest_dir / 'institution-ready-bundle.example.json'
    print(f'example={example.relative_to(ROOT)}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
