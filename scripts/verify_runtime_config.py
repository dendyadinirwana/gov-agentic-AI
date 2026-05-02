#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_KEYS = [
    'project_name', 'project_version', 'runtime_target', 'memory_mode', 'memory_policy', 'governance_mode',
    'agent_entrypoint', 'runtime_handshake', 'bootstrap_example', 'system_prompt', 'shared_guardrail_skill',
    'audit_schema', 'acceptance_tests', 'active_clusters', 'active_roles', 'active_skills',
    'knowledge_base_root', 'shared_knowledge_root', 'human_approval_required_for', 'adapter_name',
    'adapter_profile_path', 'runtime_paths', 'runtime_overrides', 'governance_policy', 'runtime_discovery',
    'runtime_installation', 'runtime_config_targets', 'default_router_role', 'default_router_alias',
    'default_router_skill', 'output_contract_required_fields', 'runtime_boot_sequence', 'runtime_pack_root',
    'central_pack_root', 'install_target_root', 'install_target_config', 'install_target_skills',
    'install_target_type', 'install_mode', 'install_applied', 'installed_at', 'government_work_logic',
    'authority_matrix', 'decision_engine', 'decision_engine_entrypoint', 'central_home_root',
    'runtime_shim_root', 'runtime_attach_mode', 'canonical_repo_root', 'shim_installed_skills',
    'canonical_skill_manifest', 'canonical_knowledge_root', 'canonical_system_prompt',
    'canonical_agent_entrypoint', 'canonical_runtime_config'
]
VALID_RUNTIMES = {'openclaw', 'hermes', 'codex', 'claude', 'antigravity', 'generic'}
VALID_MEMORY = {'local', 'mem9', 'hybrid'}
VALID_GOVERNANCE = {'sandbox', 'production'}
VALID_DISCOVERY_STATUS = {'found', 'not_found', 'not_required'}
VALID_INSTALL_TYPES = {'runtime-home', 'global-surface'}
VALID_ATTACH_MODES = {'thin-shim'}
EXPECTED_OUTPUT_FIELDS = {'summary', 'evidence_map', 'assumptions', 'confidence_status', 'red_flags', 'human_touchpoint', 'next_step'}
EXPECTED_TARGETS = {
    'hermes': '~/.hermes/gov-agentic-ai',
    'openclaw': '~/.openclaw/gov-agentic-ai',
    'claude': '~/.claude/gov-agentic-ai',
    'codex': '~/.codex/gov-agentic-ai',
    'antigravity': '~/.antigravity/gov-agentic-ai',
    'generic': '~/.agents/skills/gov-agentic-ai',
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
    validate_mcp_fields(config, errors)
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
    if config.get('install_target_type') not in VALID_INSTALL_TYPES:
        errors.append(f'invalid install_target_type: {config.get("install_target_type")}')
    if config.get('runtime_attach_mode') not in VALID_ATTACH_MODES:
        errors.append(f'invalid runtime_attach_mode: {config.get("runtime_attach_mode")}')

def validate_repo_paths(config: dict[str, Any], errors: list[str]) -> None:
    repo_relative_keys = ['agent_entrypoint', 'runtime_handshake', 'bootstrap_example', 'system_prompt', 'shared_guardrail_skill', 'audit_schema', 'acceptance_tests', 'knowledge_base_root', 'shared_knowledge_root', 'adapter_profile_path', 'government_work_logic', 'authority_matrix', 'decision_engine_entrypoint']
    for key in repo_relative_keys:
        value = config.get(key)
        if value and not (ROOT / value).exists():
            errors.append(f'path does not exist for {key}: {value}')
    for key in ['runtime_pack_root', 'central_pack_root']:
        pack_root = config.get(key)
        if pack_root and not (ROOT / pack_root).exists():
            errors.append(f'{key} does not exist: {pack_root}')

def validate_adapter(config: dict[str, Any], errors: list[str]) -> None:
    adapter = config.get('runtime_adapter', {})
    if adapter and adapter.get('adapter_name') != config.get('adapter_name'):
        errors.append('adapter_name does not match runtime_adapter.adapter_name')
    if config.get('runtime_target') != config.get('adapter_name'):
        errors.append('runtime_target should match adapter_name for current profiles')
    if not isinstance(config.get('runtime_paths'), dict) or not config['runtime_paths']:
        errors.append('runtime_paths must be a non-empty object')
    if not isinstance(config.get('runtime_overrides'), dict):
        errors.append('runtime_overrides must be an object')

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
    for skill in active_skills:
        if skill.get('name') not in skill_names:
            errors.append(f'unknown active skill: {skill.get("name")}')
    shim = set(config.get('shim_installed_skills', []))
    if 'gov-gov-ai-yayak' not in shim:
        errors.append('shim_installed_skills must include gov-gov-ai-yayak')

def validate_governance(config: dict[str, Any], errors: list[str]) -> None:
    if config.get('governance_mode') == 'production' and set(config.get('human_approval_required_for', [])) != {'L3', 'L4'}:
        errors.append('production governance must require L3 and L4 approval')
    if config.get('governance_mode') == 'sandbox' and set(config.get('human_approval_required_for', [])) != {'L4'}:
        errors.append('sandbox governance must require only L4 approval by default')

def validate_mcp_fields(config: dict[str, Any], errors: list[str]) -> None:
    mcp = config.get('mcp')
    if not isinstance(mcp, dict):
        errors.append('mcp must be an object')
        return
    mode = mcp.get('mode')
    servers = mcp.get('servers')
    if mode not in {'local', 'remote'}:
        errors.append(f'invalid mcp.mode: {mode}')
        return
    if not isinstance(servers, dict) or not servers:
        errors.append('mcp.servers must contain at least one server')
        return
    if mode == 'local':
        server = servers.get('chrome-devtools')
        if not isinstance(server, dict):
            errors.append('local mcp must include chrome-devtools server')
            return
        if server.get('transport') != 'stdio':
            errors.append('local chrome-devtools transport must be stdio')
        if 'headers' in server:
            errors.append('local mcp must not emit headers')
        if server.get('command') != 'npx':
            errors.append('local chrome-devtools command must be npx')
    if mode == 'remote':
        server = servers.get('primary')
        if not isinstance(server, dict):
            errors.append('remote mcp must include primary server')
            return
        if server.get('transport') != 'http':
            errors.append('remote mcp primary transport must be http')
        if not server.get('url'):
            errors.append('remote mcp primary server must include url')
        headers = server.get('headers')
        auth = (mcp.get('auth') or {}).get('type', 'none')
        if auth == 'none' and headers:
            errors.append('remote mcp with auth=none must not emit headers')
        if auth == 'bearer':
            if not isinstance(headers, dict) or not headers.get('Authorization'):
                errors.append('remote mcp bearer auth must emit Authorization header')
        if auth == 'x-api-key':
            if not isinstance(headers, dict) or not headers.get('x-api-key'):
                errors.append('remote mcp x-api-key auth must emit x-api-key header')
        if isinstance(headers, dict):
            for key, value in headers.items():
                if value in {'', None}:
                    errors.append(f'mcp header {key} must not be empty')

def validate_runtime_fields(config: dict[str, Any], errors: list[str]) -> None:
    decision = config.get('decision_engine')
    if not isinstance(decision, dict):
        errors.append('decision_engine must be an object')
    else:
        for key in ['enabled', 'entrypoint', 'workflow_schema', 'authority_matrix', 'rules_config', 'default_mode']:
            if key not in decision:
                errors.append(f'decision_engine missing key: {key}')
        for key in ['entrypoint', 'workflow_schema', 'authority_matrix', 'rules_config']:
            value = decision.get(key)
            if value and not (ROOT / value).exists():
                errors.append(f'decision_engine path does not exist for {key}: {value}')
    discovery = config.get('runtime_discovery')
    if not isinstance(discovery, dict):
        errors.append('runtime_discovery must be an object')
    else:
        if discovery.get('status') not in VALID_DISCOVERY_STATUS:
            errors.append(f'invalid runtime_discovery.status: {discovery.get("status")}')
        expected_fragment = EXPECTED_TARGETS[config['runtime_target']].replace('~', str(Path.home()))
        target_root = config.get('install_target_root') or ''
        if expected_fragment not in target_root and not target_root.endswith('/gov-agentic-ai'):
            errors.append(f'install_target_root must be canonical or an explicit gov-agentic-ai override for {config["runtime_target"]}: {target_root}')
    installation = config.get('runtime_installation')
    if not isinstance(installation, dict):
        errors.append('runtime_installation must be an object')
    else:
        if installation.get('mode') not in {'copy', 'advisory'}:
            errors.append('runtime_installation.mode must be copy or advisory')
    if config.get('central_home_root') != str(Path(config.get('central_home_root')).expanduser()):
        pass
    if Path(config.get('central_home_root', '')).name != '.gov-agentic-ai':
        errors.append('central_home_root must end with .gov-agentic-ai')
    if not str(config.get('canonical_skill_manifest', '')).endswith('/skills/skill_manifest.json'):
        errors.append('canonical_skill_manifest must point to central skills/skill_manifest.json')
    if not str(config.get('canonical_runtime_config', '')).endswith('/configs/runtime.generated.json'):
        errors.append('canonical_runtime_config must point to central configs/runtime.generated.json')
    for pack_key, rels in {
        'runtime_pack_root': ['runtime.generated.json', 'runtime-link.json', 'runtime-pack.manifest.json', 'skills/roles/top-layer__gov-ai_yayak/SKILL.md'],
        'central_pack_root': ['configs/runtime.generated.json', 'central-home.manifest.json', 'skills/skill_manifest.json', 'knowledge-base/kb_manifest.json'],
    }.items():
        pack_root = ROOT / config.get(pack_key, '')
        if pack_root.exists():
            for rel in rels:
                if not (pack_root / rel).exists():
                    errors.append(f'{pack_key} missing required file: {rel}')

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
    print(f'install_applied={config.get("install_applied")}')
    print(f'central_home_root={config.get("central_home_root")}')
    print(f'runtime_pack_root={config.get("runtime_pack_root")}')
    print(f'central_pack_root={config.get("central_pack_root")}')
    print(f'active_clusters={len(config.get("active_clusters", []))}')
    print(f'active_roles={len(config.get("active_roles", []))}')
    print(f'active_skills={len(config.get("active_skills", []))}')
    print(f'errors={len(errors)}')
    for error in errors:
        print(f'ERROR: {error}')

if __name__ == '__main__':
    sys.exit(main())
