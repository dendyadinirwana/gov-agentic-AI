#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_METADATA = [
    'title','role_owner','role_alias','cluster','document_type','source_unit',
    'effective_date','review_date','classification','status','summary','keywords','human_reviewer'
]
ALLOWED_PUBLISH_TARGETS = {
    '01-source-documents','02-regulations-and-policies','03-templates-and-examples',
    '04-sop-and-workflows','05-reference-data','06-output-samples','08-ingestion-ready','09-archive'
}


def load_json(path: Path):
    return json.loads(path.read_text())


def main() -> int:
    if len(sys.argv) != 2:
        print('usage: python3 scripts/verify_ingestion_bundle.py <08-ingestion-ready-dir>')
        return 2
    bundle_dir = Path(sys.argv[1]).resolve()
    errors: list[str] = []
    manifest_path = bundle_dir / 'bundle.manifest.json'
    if not manifest_path.exists():
        print('missing bundle.manifest.json')
        return 1
    manifest = load_json(manifest_path)
    for key in ['bundle_id','target_cluster','target_role_path','bundle_status','prepared_by','human_reviewer','documents']:
        if key not in manifest or manifest[key] in ('', [], None):
            errors.append(f'missing manifest field: {key}')
    docs = manifest.get('documents', [])
    if not isinstance(docs, list) or not docs:
        errors.append('documents must be a non-empty list')
    for idx, doc in enumerate(docs, start=1):
        for key in ['title','source_file','clean_file','metadata_file','document_type','publish_targets','publish_status']:
            if key not in doc or doc[key] in ('', [], None):
                errors.append(f'doc#{idx} missing field: {key}')
        source_file = bundle_dir / doc.get('source_file', '')
        clean_file = bundle_dir / doc.get('clean_file', '')
        metadata_file = bundle_dir / doc.get('metadata_file', '')
        if not source_file.exists():
            errors.append(f'doc#{idx} missing source file: {doc.get("source_file")}')
        if not clean_file.exists():
            errors.append(f'doc#{idx} missing clean file: {doc.get("clean_file")}')
        if not metadata_file.exists():
            errors.append(f'doc#{idx} missing metadata file: {doc.get("metadata_file")}')
        else:
            metadata = load_json(metadata_file)
            for field in REQUIRED_METADATA:
                if field not in metadata or metadata[field] in ('', [], None):
                    errors.append(f'doc#{idx} metadata missing field: {field}')
        for target in doc.get('publish_targets', []):
            if target not in ALLOWED_PUBLISH_TARGETS:
                errors.append(f'doc#{idx} invalid publish target: {target}')

    print(f'bundle_dir={bundle_dir}')
    print(f'document_count={len(docs)}')
    print(f'errors={len(errors)}')
    for error in errors[:100]:
        print(f'ERROR: {error}')
    return 1 if errors else 0

if __name__ == '__main__':
    raise SystemExit(main())
