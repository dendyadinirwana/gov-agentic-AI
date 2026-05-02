#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_KEYS = [
    'project_name', 'runtime_target', 'memory_mode', 'governance_mode', 'system_prompt',
    'shared_guardrail_skill', 'audit_schema', 'acceptance_tests', 'active_clusters',
    'active_roles', 'active_skills', 'knowledge_base_root', 'shared_knowledge_root',
    'human_approval_required_for', 'adapter_name', 'adapter_profile_path', 'runtime_paths',
    'runtime_overrides', 'governance_policy'
]
VALID_RUNTIMES = {'openclaw', 'hermes', 'codex', 'claude', 'antigravity', 'generic'}
VALID_MEMORY = {'local', 'mem9', 'hybrid'}
VALID_GOVERNANCE = {'sandbox', 'production'}


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'configs' / 'runtime.generated.json'
    if not path.is_absolute():
        path = ROOT / path
    errors: list[str] = []
    if not path.exists():
        errors.append(f'missing runtime config: {path}')
        report(path, {}, errors)
        return 1
    config = json.loads(path.read_text())
    for key in REQUIRED_KEYS:
        if key not in config:
            errors.append(f'missing key: {key}')
    if config.get('runtime_target') not in VALID_RUNTIMES:
        errors.append(f'invalid runtime_target: {config.get("runtime_target")}')
    if config.get('memory_mode') not in VALID_MEMORY:
        errors.append(f'invalid memory_mode: {config.get("memory_mode")}')
    if config.get('governance_mode') not in VALID_GOVERNANCE:
        errors.append(f'invalid governance_mode: {config.get("governance_mode")}')
    for key in ['system_prompt', 'shared_guardrail_skill', 'audit_schema', 'acceptance_tests', 'knowledge_base_root', 'shared_knowledge_root', 'adapter_profile_path']:
        value = config.get(key)
        if value and not (ROOT / value).exists():
            errors.append(f'path does not exist for {key}: {value}')
    adapter = config.get('runtime_adapter', {})
    if adapter and adapter.get('adapter_name') != config.get('adapter_name'):
        errors.append('adapter_name does not match runtime_adapter.adapter_name')
    if config.get('runtime_target') != config.get('adapter_name'):
        errors.append('runtime_target should match adapter_name for current profiles')
    kb = json.loads((ROOT / 'knowledge-base' / 'kb_manifest.json').read_text())
    skills = json.loads((ROOT / 'skills' / 'skill_manifest.json').read_text())
    valid_clusters = {role['cluster'] for role in kb['roles']}
    active_clusters = set(config.get('active_clusters', []))
    if not active_clusters:
        errors.append('active_clusters must not be empty')
    for cluster in active_clusters:
        if cluster not in valid_clusters:
            errors.append(f'unknown active cluster: {cluster}')
    expected_roles = [role for role in kb['roles'] if role['cluster'] in active_clusters]
    active_roles = config.get('active_roles', [])
    active_skills = config.get('active_skills', [])
    if len(active_roles) != len(expected_roles):
        errors.append(f'active_roles count {len(active_roles)} != expected {len(expected_roles)}')
    skill_names = {skill['name'] for skill in skills['skills']}
    for skill in active_skills:
        if skill.get('name') not in skill_names:
            errors.append(f'unknown active skill: {skill.get("name")}')
        if skill.get('skill_md') and not (ROOT / skill['skill_md']).exists():
            errors.append(f'missing active skill md: {skill.get("skill_md")}')
    gov = config.get('governance_policy', {})
    if config.get('governance_mode') == 'production' and set(config.get('human_approval_required_for', [])) != {'L3', 'L4'}:
        errors.append('production governance must require L3 and L4 approval')
    if config.get('governance_mode') == 'sandbox' and set(config.get('human_approval_required_for', [])) != {'L4'}:
        errors.append('sandbox governance must require only L4 approval by default')
    if 'mode_summary' not in gov:
        errors.append('governance_policy.mode_summary missing')
    if 'runtime_paths' not in config or not isinstance(config['runtime_paths'], dict):
        errors.append('runtime_paths must be present and be an object')
    report(path, config, errors)
    return 1 if errors else 0


def report(path: Path, config: dict, errors: list[str]) -> None:
    print(f'config={path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}')
    print(f'runtime_target={config.get("runtime_target")}')
    print(f'adapter_name={config.get("adapter_name")}')
    print(f'memory_mode={config.get("memory_mode")}')
    print(f'governance_mode={config.get("governance_mode")}')
    print(f'active_clusters={len(config.get("active_clusters", []))}')
    print(f'active_roles={len(config.get("active_roles", []))}')
    print(f'active_skills={len(config.get("active_skills", []))}')
    print(f'errors={len(errors)}')
    for error in errors:
        print(f'ERROR: {error}')

if __name__ == '__main__':
    sys.exit(main())
