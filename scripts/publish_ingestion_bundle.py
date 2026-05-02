#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / 'knowledge-base'
PUBLISHABLE_TARGETS = {
    '01-source-documents',
    '02-regulations-and-policies',
    '03-templates-and-examples',
    '04-sop-and-workflows',
    '05-reference-data',
    '06-output-samples',
    '08-ingestion-ready',
}
ARCHIVE_TARGET = '09-archive'


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def slugify(text: str) -> str:
    safe = ''.join(ch.lower() if ch.isalnum() else '-' for ch in text)
    while '--' in safe:
        safe = safe.replace('--', '-')
    return safe.strip('-') or 'document'


def archive_existing(target_file: Path, archive_dir: Path, dry_run: bool) -> Path:
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    archived_name = f"{target_file.stem}__replaced_{timestamp}{target_file.suffix}"
    archived_path = archive_dir / archived_name
    if dry_run:
        return archived_path
    archive_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(target_file), str(archived_path))
    return archived_path


def ensure_bundle_verified(bundle_dir: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / 'scripts' / 'verify_ingestion_bundle.py'), str(bundle_dir)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f'bundle verification failed:\n{result.stdout}{result.stderr}')


def publish(bundle_dir: Path, dry_run: bool, archive_existing_files: bool) -> tuple[list[str], list[str]]:
    manifest_path = bundle_dir / 'bundle.manifest.json'
    if not manifest_path.exists():
        raise RuntimeError('missing bundle.manifest.json')
    manifest = load_json(manifest_path)
    if manifest.get('bundle_status') != 'approved':
        raise RuntimeError("bundle_status must be 'approved' before publish")
    target_role = manifest['target_role_path']
    role_root = KB / target_role
    if not role_root.exists():
        raise RuntimeError(f'target role path not found: {target_role}')

    ensure_bundle_verified(bundle_dir)

    published: list[str] = []
    archived: list[str] = []

    for doc in manifest.get('documents', []):
        if doc.get('publish_status') not in {'approved', 'ready'}:
            continue
        source_file = bundle_dir / doc['source_file']
        metadata_file = bundle_dir / doc['metadata_file']
        metadata = load_json(metadata_file)
        base_name = slugify(metadata.get('title', doc.get('title', 'document')))
        source_ext = source_file.suffix or '.md'

        for target in doc.get('publish_targets', []):
            if target not in PUBLISHABLE_TARGETS:
                raise RuntimeError(f'invalid publish target for publisher: {target}')
            destination_dir = role_root / target
            destination_dir.mkdir(parents=True, exist_ok=True)
            destination_file = destination_dir / f'{base_name}{source_ext}'
            destination_metadata = destination_dir / f'{base_name}.metadata.json'

            if archive_existing_files:
                if destination_file.exists():
                    archived_path = archive_existing(destination_file, role_root / ARCHIVE_TARGET, dry_run)
                    archived.append(str(archived_path.relative_to(ROOT)))
                if destination_metadata.exists():
                    archived_meta = archive_existing(destination_metadata, role_root / ARCHIVE_TARGET, dry_run)
                    archived.append(str(archived_meta.relative_to(ROOT)))
            elif destination_file.exists() or destination_metadata.exists():
                raise RuntimeError(f'destination already exists, rerun with --archive-existing: {destination_file.relative_to(ROOT)}')

            if dry_run:
                published.append(str(destination_file.relative_to(ROOT)))
                published.append(str(destination_metadata.relative_to(ROOT)))
            else:
                shutil.copyfile(source_file, destination_file)
                shutil.copyfile(metadata_file, destination_metadata)
                published.append(str(destination_file.relative_to(ROOT)))
                published.append(str(destination_metadata.relative_to(ROOT)))

    return published, archived


def main() -> int:
    parser = argparse.ArgumentParser(description='Publish an approved ingestion bundle into role knowledge folders.')
    parser.add_argument('bundle_dir', help='Path to the role 08-ingestion-ready directory containing bundle.manifest.json')
    parser.add_argument('--dry-run', action='store_true', help='Print what would be published without writing files')
    parser.add_argument('--archive-existing', action='store_true', help='Archive existing target files into 09-archive before replacement')
    parser.add_argument('--refresh-quality', action='store_true', help='Run generate_role_knowledge.py after publish to refresh quality manifest')
    args = parser.parse_args()

    bundle_dir = Path(args.bundle_dir).resolve()
    try:
        published, archived = publish(bundle_dir, dry_run=args.dry_run, archive_existing_files=args.archive_existing)
    except RuntimeError as exc:
        print(f'ERROR: {exc}')
        return 1

    print(f'bundle_dir={bundle_dir}')
    print(f'dry_run={str(args.dry_run).lower()}')
    print(f'published_count={len(published)}')
    print(f'archived_count={len(archived)}')
    for item in archived:
        print(f'ARCHIVED: {item}')
    for item in published:
        print(f'PUBLISH: {item}')

    if args.refresh_quality and not args.dry_run:
        result = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'generate_role_knowledge.py')], cwd=ROOT)
        if result.returncode != 0:
            print('ERROR: generate_role_knowledge.py failed after publish')
            return result.returncode
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
