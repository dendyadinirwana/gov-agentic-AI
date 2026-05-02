#!/usr/bin/env python3
from pathlib import Path
import json, sys

root = Path(__file__).resolve().parents[1]
kb = root / 'knowledge-base'
required_root = [
    'README.md', 'AGENT_README.md', '.gitignore',
    'docs/deliverables/README.md',
    'docs/deliverables/Gov_Agentic_AI_v3.1_Implementation_Pack.docx',
    'docs/deliverables/Gov_Agentic_AI_v3.0_Master_Full.docx',
    'docs/deliverables/Gov_Agentic_AI_v3.0_Knowledge_UseCases.docx',
    'docs/governance/Gov_Agentic_AI_v3.1_Implementation_Pack.md',
    'docs/operations/REPLICATION_GUIDE.md',
    'docs/knowledge-model/SHARED_VS_ROLE_KNOWLEDGE.md',
    'docs/knowledge-model/KNOWLEDGE_AUTHORING_GUIDE.md',
    'docs/architecture/GOVERNMENT_WORK_LOGIC.md',
    'prompts/system/YayakAI_Master_System_Prompt_v3.0.md',
    'skills/_shared/gov-agentic-common/references/government-work-logic.md',
    'schemas/audit_log_template_v3.0.json',
    'schemas/Gov_Agentic_AI_v3.1_Acceptance_Tests.json',
    'schemas/authority_matrix.schema.json',
    'schemas/government_workflow_state.schema.json',
    'configs/government_logic_rules.json',
    'configs/authority_matrix.json',
    'knowledge-base/kb_manifest.json',
    'knowledge-base/knowledge_quality_manifest.json',
    'knowledge-base/INGESTION_GUIDE.md',
    'knowledge-base/_shared/README.md',
    'knowledge-base/_shared/07-ingestion-staging/bundle.manifest.template.json',
    'docs/operations/INSTITUTION_INGESTION_PACK.md',
    'docs/operations/GOVERNMENT_DECISION_ENGINE.md',
    'docs/operations/KNOWLEDGE_OPS_REPORT.md',
    'docs/operations/UNINSTALL_GUIDE.md',
    'runtime-adapters/universal/RUNTIME_HANDSHAKE.md',
    'examples/BOOTSTRAP_EXAMPLE.json',
    'scripts/uninstall_gov_agentic_ai.py',
    'scripts/verify_central_home.py',
    'docs/operations/knowledge_ops_report.json',
    'scripts/generate_role_knowledge.py',
    'scripts/verify_knowledge_base.py',
    'scripts/scaffold_ingestion_bundle.py',
    'scripts/verify_ingestion_bundle.py',
    'scripts/publish_ingestion_bundle.py',
    'scripts/knowledge_ops_report.py',
    'scripts/government_decision_engine.py',
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
outside_repo = []
absolute_links = []
for p in kb.rglob('*'):
    if p.is_symlink() and not p.exists():
        broken.append(str(p.relative_to(root)))
    if p.is_symlink():
        link_target = p.readlink()
        if link_target.is_absolute():
            absolute_links.append(str(p.relative_to(root)))
        try:
            p.resolve(strict=False).relative_to(root.resolve())
        except ValueError:
            outside_repo.append(str(p.relative_to(root)))

print(f"roles={manifest['role_count']}")
print(f"broken_symlinks={len(broken)}")
print(f"absolute_symlinks={len(absolute_links)}")
print(f"outside_repo_symlinks={len(outside_repo)}")
print(f"missing_required={len(missing)}")
if missing:
    print('MISSING:')
    print('\n'.join(missing[:100]))
if broken:
    print('BROKEN SYMLINKS:')
    print('\n'.join(broken[:100]))
if absolute_links:
    print('ABSOLUTE SYMLINKS:')
    print('\n'.join(absolute_links[:100]))
if outside_repo:
    print('OUTSIDE REPO SYMLINKS:')
    print('\n'.join(outside_repo[:100]))
sys.exit(1 if missing or broken or absolute_links or outside_repo else 0)
