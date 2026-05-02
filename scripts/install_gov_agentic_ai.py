#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
KB_MANIFEST = ROOT / 'knowledge-base' / 'kb_manifest.json'
SKILL_MANIFEST = ROOT / 'skills' / 'skill_manifest.json'
DEFAULTS_PATH = ROOT / 'configs' / 'installer.defaults.json'
DEFAULT_OUTPUT = ROOT / 'configs' / 'runtime.generated.json'
DEFAULT_ACTIVE_DEPLOYMENT = ROOT / 'configs' / 'active.deployment.yaml'

RUNTIMES = ['openclaw', 'hermes', 'codex', 'claude', 'antigravity', 'generic']
MEMORY_MODES = ['local', 'mem9', 'hybrid']
GOVERNANCE_MODES = ['sandbox', 'production']


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def prompt_choice(label: str, options: list[str], default: str) -> str:
    print(f'\n{label}')
    for idx, option in enumerate(options, 1):
        marker = ' (default)' if option == default else ''
        print(f'  {idx}. {option}{marker}')
    raw = input('Choose number or value: ').strip()
    if not raw:
        return default
    if raw.isdigit() and 1 <= int(raw) <= len(options):
        return options[int(raw) - 1]
    if raw in options:
        return raw
    print(f'Invalid choice: {raw}', file=sys.stderr)
    return prompt_choice(label, options, default)


def prompt_clusters(clusters: list[str], default_all: bool = True) -> list[str]:
    print('\nCluster activation')
    for idx, cluster in enumerate(clusters, 1):
        print(f'  {idx}. {cluster}')
    print('Enter comma-separated numbers/names, or press Enter for all clusters.')
    raw = input('Clusters: ').strip()
    if not raw and default_all:
        return clusters
    selected: list[str] = []
    for part in [p.strip() for p in raw.split(',') if p.strip()]:
        if part.isdigit() and 1 <= int(part) <= len(clusters):
            selected.append(clusters[int(part) - 1])
        elif part in clusters:
            selected.append(part)
        else:
            raise SystemExit(f'Unknown cluster selection: {part}')
    return dedupe(selected)


def dedupe(values: list[str]) -> list[str]:
    seen = set()
    out = []
    for value in values:
        if value not in seen:
            out.append(value)
            seen.add(value)
    return out


def parse_csv(value: str | None) -> list[str] | None:
    if value is None:
        return None
    return [part.strip() for part in value.split(',') if part.strip()]


def build_config(runtime: str, memory: str, governance: str, active_clusters: list[str]) -> dict[str, Any]:
    kb = load_json(KB_MANIFEST)
    skills = load_json(SKILL_MANIFEST)
    role_rows = kb['roles']
    skill_by_role = {(s['cluster'], s['role'], s['alias']): s for s in skills['skills']}
    active_roles = []
    active_skills = []
    for role in role_rows:
        if role['cluster'] not in active_clusters:
            continue
        skill = skill_by_role[(role['cluster'], role['role'], role['alias'])]
        active_roles.append({
            'cluster': role['cluster'],
            'role': role['role'],
            'alias': role['alias'],
            'knowledge_path': str(role.get('path') and Path(kb['base_path']) / role['path']),
            'skill_name': skill['name'],
            'skill_path': skill['skill_path'],
            'prompt_path': skill['prompt_path'],
        })
        active_skills.append({
            'name': skill['name'],
            'skill_path': skill['skill_path'],
            'skill_md': skill['skill_md'],
            'role': skill['role'],
            'alias': skill['alias'],
            'cluster': skill['cluster'],
        })
    return {
        'project_name': 'gov-agentic-ai',
        'runtime_target': runtime,
        'memory_mode': memory,
        'memory_policy': memory_policy(memory),
        'governance_mode': governance,
        'system_prompt': 'prompts/system/YayakAI_Master_System_Prompt_v3.0.md',
        'default_router_role': 'GOV-AI',
        'default_router_alias': 'Yayak',
        'default_router_skill': 'gov-gov-ai-yayak',
        'shared_guardrail_skill': skills['shared_skill'],
        'audit_schema': 'schemas/audit_log_template_v3.0.json',
        'acceptance_tests': 'schemas/Gov_Agentic_AI_v3.1_Acceptance_Tests.json',
        'knowledge_base_root': kb['base_path'],
        'shared_knowledge_root': 'knowledge-base/_shared',
        'active_clusters': active_clusters,
        'active_roles': active_roles,
        'active_skills': active_skills,
        'human_approval_required_for': ['L3', 'L4'] if governance == 'production' else ['L4'],
        'output_contract_required_fields': [
            'summary', 'evidence_map', 'assumptions', 'confidence_status', 'red_flags', 'human_touchpoint', 'next_step'
        ],
        'runtime_boot_sequence': [
            'read_runtime_config',
            'load_system_prompt',
            'load_shared_guardrail_skill',
            'default_to_yayak_router',
            'select_only_active_roles_and_skills',
            'retrieve_active_role_and_shared_knowledge',
            'apply_memory_policy',
            'emit_required_output_contract',
            'require_hitl_for_configured_action_levels',
        ],
    }


def memory_policy(memory: str) -> dict[str, str]:
    if memory == 'local':
        return {
            'canonical_knowledge': 'local knowledge-base only',
            'working_memory': 'runtime-local memory only',
            'external_memory': 'disabled by default',
        }
    if memory == 'mem9':
        return {
            'canonical_knowledge': 'mem9 primary memory surface',
            'working_memory': 'mem9 session and preference memory',
            'external_memory': 'mem9 required',
        }
    return {
        'canonical_knowledge': 'local knowledge-base is source of truth',
        'working_memory': 'mem9 stores preferences, session memory, and operational recall',
        'external_memory': 'mem9 optional but expected',
    }


def write_yaml_like(path: Path, config: dict[str, Any]) -> None:
    lines = [
        f"project_name: {config['project_name']}",
        f"runtime_target: {config['runtime_target']}",
        f"memory_mode: {config['memory_mode']}",
        f"governance_mode: {config['governance_mode']}",
        f"system_prompt: {config['system_prompt']}",
        f"shared_guardrail_skill: {config['shared_guardrail_skill']}",
        f"audit_schema: {config['audit_schema']}",
        f"acceptance_tests: {config['acceptance_tests']}",
        f"knowledge_base_root: {config['knowledge_base_root']}",
        f"shared_knowledge_root: {config['shared_knowledge_root']}",
        'human_approval_required_for:',
    ]
    lines.extend(f"  - {item}" for item in config['human_approval_required_for'])
    lines.append('active_clusters:')
    lines.extend(f"  - {item}" for item in config['active_clusters'])
    lines.append('active_role_count: ' + str(len(config['active_roles'])))
    lines.append('active_skill_count: ' + str(len(config['active_skills'])))
    path.write_text('\n'.join(lines) + '\n')


def main() -> None:
    parser = argparse.ArgumentParser(description='Interactive installer for Gov-Agentic AI runtime config.')
    parser.add_argument('--defaults', action='store_true', help='Use installer defaults without prompts.')
    parser.add_argument('--runtime', choices=RUNTIMES, help='Runtime target.')
    parser.add_argument('--memory', choices=MEMORY_MODES, help='Memory mode.')
    parser.add_argument('--governance', choices=GOVERNANCE_MODES, help='Governance mode.')
    parser.add_argument('--clusters', help='Comma-separated active clusters. Default: all clusters.')
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT), help='Runtime JSON output path.')
    parser.add_argument('--active-deployment', default=str(DEFAULT_ACTIVE_DEPLOYMENT), help='YAML summary output path.')
    args = parser.parse_args()

    defaults = load_json(DEFAULTS_PATH) if DEFAULTS_PATH.exists() else {}
    kb = load_json(KB_MANIFEST)
    clusters = sorted({role['cluster'] for role in kb['roles']})

    if args.defaults:
        runtime = args.runtime or defaults.get('runtime_target', 'generic')
        memory = args.memory or defaults.get('memory_mode', 'hybrid')
        governance = args.governance or defaults.get('governance_mode', 'production')
        active_clusters = parse_csv(args.clusters) or defaults.get('active_clusters') or clusters
    else:
        runtime = args.runtime or prompt_choice('Runtime target', RUNTIMES, defaults.get('runtime_target', 'generic'))
        memory = args.memory or prompt_choice('Memory mode', MEMORY_MODES, defaults.get('memory_mode', 'hybrid'))
        governance = args.governance or prompt_choice('Governance mode', GOVERNANCE_MODES, defaults.get('governance_mode', 'production'))
        active_clusters = parse_csv(args.clusters) or prompt_clusters(clusters)

    unknown = sorted(set(active_clusters) - set(clusters))
    if unknown:
        raise SystemExit(f'Unknown clusters: {", ".join(unknown)}')

    config = build_config(runtime, memory, governance, active_clusters)
    output = (ROOT / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    active_deployment = (ROOT / args.active_deployment).resolve() if not Path(args.active_deployment).is_absolute() else Path(args.active_deployment)
    output.parent.mkdir(parents=True, exist_ok=True)
    active_deployment.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n')
    write_yaml_like(active_deployment, config)

    print(f'wrote_runtime_config={output.relative_to(ROOT) if output.is_relative_to(ROOT) else output}')
    print(f'wrote_active_deployment={active_deployment.relative_to(ROOT) if active_deployment.is_relative_to(ROOT) else active_deployment}')
    print(f'runtime_target={runtime}')
    print(f'memory_mode={memory}')
    print(f'governance_mode={governance}')
    print(f'active_clusters={len(active_clusters)}')
    print(f'active_roles={len(config["active_roles"])}')
    print(f'active_skills={len(config["active_skills"])}')

if __name__ == '__main__':
    main()
