#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / 'knowledge-base'
MANIFEST = KB / 'kb_manifest.json'
QUALITY = KB / 'knowledge_quality_manifest.json'
REQUIRED = [
    '00-readme/role-charter.md',
    '01-source-documents/source-map.md',
    '02-regulations-and-policies/policy-map.md',
    '03-templates-and-examples/artifact-catalog.md',
    '04-sop-and-workflows/workflow-map.md',
    '04-sop-and-workflows/decision-boundaries.md',
    '05-reference-data/reference-catalog.md',
    '06-output-samples/starter-output-examples.md',
    '07-review-notes/quality-checklist.md',
    '08-ingestion-ready/intake-guide.md',
    '09-archive/archive-rules.md',
]
SHARED_REQUIRED = [
    '00-governance-and-routing/role-routing-matrix.md',
    '01-regulasi-umum/source-hierarchy.md',
    '02-sop-umum/sop-primitives.md',
    '03-template-global/global-artifact-patterns.md',
    '04-data-dictionaries/common-data-dictionary.md',
    '05-risk-and-compliance/risk-trigger-matrix.md',
    '06-audit-and-observability/audit-observability-contract.md',
    '08-golden-outputs/golden-output-patterns.md',
]


def near_empty(path: Path) -> bool:
    if not path.exists():
        return True
    text = path.read_text().strip()
    return len(text) < 160


def main() -> int:
    kb_manifest = json.loads(MANIFEST.read_text())
    errors: list[str] = []
    missing_starter_docs = 0
    near_empty_sections = 0
    broken_shared_links = 0
    missing_output_examples = 0
    weak_roles = 0

    if not QUALITY.exists():
        errors.append('missing knowledge-base/knowledge_quality_manifest.json')

    for rel in SHARED_REQUIRED:
        path = KB / '_shared' / rel
        if not path.exists():
            errors.append(f'missing shared starter file: knowledge-base/_shared/{rel}')

    for role in kb_manifest['roles']:
        role_dir = KB / role['path']
        role_missing = False
        for rel in REQUIRED:
            path = role_dir / rel
            if not path.exists():
                missing_starter_docs += 1
                role_missing = True
                errors.append(f'missing starter doc: {path.relative_to(ROOT)}')
            elif near_empty(path):
                near_empty_sections += 1
                errors.append(f'near-empty starter doc: {path.relative_to(ROOT)}')
        output_sample = role_dir / '06-output-samples' / 'starter-output-examples.md'
        if not output_sample.exists() or near_empty(output_sample):
            missing_output_examples += 1
        shared_links = role_dir / '_shared-links'
        if not shared_links.exists():
            broken_shared_links += 1
            role_missing = True
            errors.append(f'missing _shared-links: {shared_links.relative_to(ROOT)}')
        else:
            for link in shared_links.iterdir():
                if link.is_symlink() and not link.exists():
                    broken_shared_links += 1
                    role_missing = True
                    errors.append(f'broken shared symlink: {link.relative_to(ROOT)}')
        if role_missing:
            weak_roles += 1

    role_count = kb_manifest['role_count']
    print(f'role_count={role_count}')
    print(f'missing_starter_docs={missing_starter_docs}')
    print(f'near_empty_sections={near_empty_sections}')
    print(f'broken_shared_links={broken_shared_links}')
    print(f'missing_output_examples={missing_output_examples}')
    print(f'weak_roles={weak_roles}')
    print(f'errors={len(errors)}')
    for error in errors[:120]:
        print(f'ERROR: {error}')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
