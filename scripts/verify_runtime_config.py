#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_KEYS = [
    'project_name', 'runtime_target', 'memory_mode', 'memory_policy', 'governance_mode',
    'system_prompt', 'shared_guardrail_skill', 'audit_schema', 'acceptance_tests',
    'active_clusters', 'active_roles', 'active_skills', 'knowledge_base_root',
    'shared_knowledge_root', 'human_approval_required_for', 'adapter_name',
    'adapter_profile_path', 'runtime_paths', 'runtime_overrides', 'governance_policy',
    'runtime_discovery', 'runtime_installation', 'runtime_config_targets',
    'default_router_role', 'default_router_alias', 'default_router_skill',
    'output_contract_required_fields', 'runtime_boot_sequence'
]
VALID_RUNTIMES = {'openclaw', 'hermes', 'codex', 'claude', 'antigravity', 'generic'}
VALID_MEMORY = {'local', 'mem9', 'hybrid'}
VALID_GOVERNANCE = {'sandbox', 'production'}
VALID_DISCOVERY_STATUS = {'found', 'not_found', 'not_required'}
EXPECTED_OUTPUT_FIELDS = {
    'summary', 'evidence_map', 'assumptions', 'confidence_status',
    'red_flags', 'human_touchpoint', 'next_step'
}


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

    validate_enums(config, errors)
    validate_repo_paths(config, errors)
    validate_adapter(config, errors)
    validate_inventory(config, errors)
    validate_governance(config, errors)
    validate_runtime_fields(config, errors)
    validate_output_contract(config, errors)

    report(path, config, errors)
    return 1 if errors else 0


def validate_enums(config: dict[str, Any], errors: list[str]) -> None:
    if config.get('runtime_target') not in VALID_RUNTIMES:
        errors.append(f'invalid runtime_target: {config.get("runtime_target")}')
    if config.get('memory_mode') not in VALID_MEMORY:
        errors.append(f'invalid memory_mode: {config.get("memory_mode")}')
    if config.get('governance_mode') not in VALID_GOVERNANCE:
        errors.append(f'invalid governance_mode: {config.get("governance_mode")}')


def validate_repo_paths(config: dict[str, Any], errors: list[str]) -> None:
    repo_relative_keys = [
        'system_prompt', 'shared_guardrail_skill', 'audit_schema', 'acceptance_tests',
        'knowledge_base_root', 'shared_knowledge_root', 'adapter_profile_path'
    ]
    for key in repo_relative_keys:
        value = config.get(key)
        if value and not (ROOT / value).exists():
            errors.append(f'path does not exist for {key}: {value}')


def validate_adapter(config: dict[str, Any], errors: list[str]) -> None:
    adapter = config.get('runtime_adapter', {})
    if adapter and adapter.get('adapter_name') != config.get('adapter_name'):
        errors.append('adapter_name does not match runtime_adapter.adapter_name')
    if config.get('runtime_target') != config.get('adapter_name'):
        errors.append('runtime_target should match adapter_name for current profiles')
    runtime_paths = config.get('runtime_paths')
    if not isinstance(runtime_paths, dict) or not runtime_paths:
        errors.append('runtime_paths must be present and be a non-empty object')
    runtime_overrides = config.get('runtime_overrides')
    if not isinstance(runtime_overrides, dict):
        errors.append('runtime_overrides must be present and be an object')


def validate_inventory(config: dict[str, Any], errors: list[str]) -> None:
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
    if len(active_skills) != len(expected_roles):
        errors.append(f'active_skills count {len(active_skills)} != expected {len(expected_roles)}')
    skill_names = {skill['name'] for skill in skills['skills']}
    for role in active_roles:
        for required_key in ['cluster', 'role', 'alias', 'knowledge_path', 'skill_name', 'skill_path', 'prompt_path']:
            if required_key not in role:
                errors.append(f'active_role missing key: {required_key}')
        knowledge_path = role.get('knowledge_path')
        if knowledge_path and not (ROOT / knowledge_path).exists():
            errors.append(f'missing active role knowledge path: {knowledge_path}')
        prompt_path = role.get('prompt_path')
        if prompt_path and not (ROOT / prompt_path).exists():
            errors.append(f'missing active role prompt path: {prompt_path}')
    for skill in active_skills:
        if skill.get('name') not in skill_names:
            errors.append(f'unknown active skill: {skill.get("name")}')
        for key in ['skill_path', 'skill_md']:
            value = skill.get(key)
            if value and not (ROOT / value).exists():
                errors.append(f'missing active skill path for {key}: {value}')


def validate_governance(config: dict[str, Any], errors: list[str]) -> None:
    gov = config.get('governance_policy', {})
    if not isinstance(gov, dict):
        errors.append('governance_policy must be an object')
        return
    if 'mode_summary' not in gov:
        errors.append('governance_policy.mode_summary missing')
    if config.get('governance_mode') == 'production' and set(config.get('human_approval_required_for', [])) != {'L3', 'L4'}:
        errors.append('production governance must require L3 and L4 approval')
    if config.get('governance_mode') == 'sandbox' and set(config.get('human_approval_required_for', [])) != {'L4'}:
        errors.append('sandbox governance must require only L4 approval by default')


def validate_runtime_fields(config: dict[str, Any], errors: list[str]) -> None:
    discovery = config.get('runtime_discovery')
    if not isinstance(discovery, dict):
        errors.append('runtime_discovery must be an object')
    else:
        status = discovery.get('status')
        if status not in VALID_DISCOVERY_STATUS:
            errors.append(f'invalid runtime_discovery.status: {status}')
        for key in ['candidate_paths', 'discovered_paths']:
            if not isinstance(discovery.get(key), list):
                errors.append(f'runtime_discovery.{key} must be a list')
        if discovery.get('selected_runtime_home') and not Path(discovery['selected_runtime_home']).exists():
            errors.append(f'runtime_discovery.selected_runtime_home does not exist: {discovery["selected_runtime_home"]}')

    installation = config.get('runtime_installation')
    if not isinstance(installation, dict):
        errors.append('runtime_installation must be an object')
    else:
        if installation.get('mode') != 'advisory':
            errors.append('runtime_installation.mode must currently be advisory')
        if installation.get('writes_external_runtime_config') not in {True, False}:
            errors.append('runtime_installation.writes_external_runtime_config must be boolean')

    targets = config.get('runtime_config_targets')
    if not isinstance(targets, dict):
        errors.append('runtime_config_targets must be an object')
    else:
        for key in ['repo_local', 'active_deployment', 'write_runtime_config_default']:
            if key not in targets:
                errors.append(f'runtime_config_targets missing key: {key}')
        repo_local = targets.get('repo_local')
        if repo_local and repo_local != 'configs/runtime.generated.json':
            errors.append('runtime_config_targets.repo_local must point to configs/runtime.generated.json')

    boot_sequence = config.get('runtime_boot_sequence')
    if not isinstance(boot_sequence, list) or not boot_sequence:
        errors.append('runtime_boot_sequence must be a non-empty list')


def validate_output_contract(config: dict[str, Any], errors: list[str]) -> None:
    fields = set(config.get('output_contract_required_fields', []))
    if fields != EXPECTED_OUTPUT_FIELDS:
        errors.append('output_contract_required_fields does not match expected contract')
    if config.get('default_router_alias') != 'Yayak':
        errors.append('default_router_alias must remain Yayak')


def report(path: Path, config: dict[str, Any], errors: list[str]) -> None:
    print(f'config={path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}')
    print(f'runtime_target={config.get("runtime_target")}')
    print(f'adapter_name={config.get("adapter_name")}')
    print(f'memory_mode={config.get("memory_mode")}')
    print(f'governance_mode={config.get("governance_mode")}')
    print(f'discovery_status={config.get("runtime_discovery", {}).get("status")}')
    print(f'active_clusters={len(config.get("active_clusters", []))}')
    print(f'active_roles={len(config.get("active_roles", []))}')
    print(f'active_skills={len(config.get("active_skills", []))}')
    print(f'errors={len(errors)}')
    for error in errors:
        print(f'ERROR: {error}')


if __name__ == '__main__':
    sys.exit(main())
