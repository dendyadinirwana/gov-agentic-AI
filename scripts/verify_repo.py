#!/usr/bin/env python3
from pathlib import Path
import json, sys

root = Path(__file__).resolve().parents[1]
kb = root / 'knowledge-base'
required_root = [
    'README.md', '.gitignore',
    'docs/governance/Gov_Agentic_AI_v3.1_Implementation_Pack.md',
    'docs/operations/REPLICATION_GUIDE.md',
    'docs/knowledge-model/SHARED_VS_ROLE_KNOWLEDGE.md',
    'docs/knowledge-model/KNOWLEDGE_AUTHORING_GUIDE.md',
    'prompts/system/YayakAI_Master_System_Prompt_v3.0.md',
    'schemas/audit_log_template_v3.0.json',
    'schemas/Gov_Agentic_AI_v3.1_Acceptance_Tests.json',
    'knowledge-base/kb_manifest.json',
    'knowledge-base/knowledge_quality_manifest.json',
    'knowledge-base/INGESTION_GUIDE.md',
    'knowledge-base/_shared/README.md',
    'knowledge-base/_shared/07-ingestion-staging/bundle.manifest.template.json',
    'docs/operations/INSTITUTION_INGESTION_PACK.md',
    'scripts/generate_role_knowledge.py',
    'scripts/verify_knowledge_base.py',
    'scripts/scaffold_ingestion_bundle.py',
    'scripts/verify_ingestion_bundle.py',
    'scripts/publish_ingestion_bundle.py',
]
missing = []
for rel in required_root:
    if not (root / rel).exists():
        missing.append(rel)
manifest = json.loads((kb / 'kb_manifest.json').read_text())
for role in manifest['roles']:
    role_dir = kb / role['path']
    for sub in manifest['standard_subdirectories']:
        if not (role_dir / sub).is_dir():
            missing.append(str((role_dir / sub).relative_to(root)))
    if not (role_dir / '_shared-links').is_dir():
        missing.append(str((role_dir / '_shared-links').relative_to(root)))

broken = []
for p in kb.rglob('*'):
    if p.is_symlink() and not p.exists():
        broken.append(str(p.relative_to(root)))

print(f"roles={manifest['role_count']}")
print(f"broken_symlinks={len(broken)}")
print(f"missing_required={len(missing)}")
if missing:
    print('MISSING:')
    print('\n'.join(missing[:100]))
if broken:
    print('BROKEN SYMLINKS:')
    print('\n'.join(broken[:100]))
sys.exit(1 if missing or broken else 0)
