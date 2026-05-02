#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, TextIO

ROOT = Path(__file__).resolve().parents[1]
KB_MANIFEST = ROOT / 'knowledge-base' / 'kb_manifest.json'
SKILL_MANIFEST = ROOT / 'skills' / 'skill_manifest.json'
DEFAULTS_PATH = ROOT / 'configs' / 'installer.defaults.json'
DEFAULT_OUTPUT = ROOT / 'configs' / 'runtime.generated.json'
DEFAULT_ACTIVE_DEPLOYMENT = ROOT / 'configs' / 'active.deployment.yaml'

RUNTIMES = ['openclaw', 'hermes', 'codex', 'claude', 'antigravity', 'generic']
MEMORY_MODES = ['local', 'mem9', 'hybrid']
GOVERNANCE_MODES = ['sandbox', 'production']

RUNTIME_DISCOVERY_CANDIDATES = {
    'generic': {},
    'hermes': {
        'Darwin': ['~/Library/Application Support/Hermes', '~/.hermes', '~/.config/hermes'],
        'Linux': ['~/.config/hermes', '~/.hermes'],
        'Windows': ['%APPDATA%/Hermes', '%USERPROFILE%/.hermes'],
    },
    'openclaw': {
        'Darwin': ['~/.openclaw', '~/.config/openclaw'],
        'Linux': ['~/.config/openclaw', '~/.openclaw'],
        'Windows': ['%APPDATA%/OpenClaw', '%USERPROFILE%/.openclaw'],
    },
    'codex': {
        'Darwin': ['${CODEX_HOME}', '~/.codex'],
        'Linux': ['${CODEX_HOME}', '~/.codex'],
        'Windows': ['%CODEX_HOME%', '%USERPROFILE%/.codex'],
    },
    'claude': {
        'Darwin': ['~/.claude', '~/Library/Application Support/Claude'],
        'Linux': ['~/.claude', '~/.config/claude'],
        'Windows': ['%APPDATA%/Claude', '%USERPROFILE%/.claude'],
    },
    'antigravity': {
        'Darwin': ['~/.antigravity', '~/.config/antigravity'],
        'Linux': ['~/.config/antigravity', '~/.antigravity'],
        'Windows': ['%APPDATA%/Antigravity', '%USERPROFILE%/.antigravity'],
    },
}

ANSI_CLEAR = '\033[2J\033[H'
ANSI_RESET = '\033[0m'
ANSI_ACTIVE = '\033[7m'
ANSI_DIM = '\033[2m'
ANSI_CYAN = '\033[96m'
ANSI_BLUE = '\033[94m'
ANSI_MAGENTA = '\033[95m'
ANSI_BOLD = '\033[1m'




GOV_AGENT_ASCII = [
    "  e88'Y88    e88 88e   Y8b Y88888P         e Y8b       e88'Y88  888'Y88 Y88b Y88 88P'888'Y88 ",
    " d888  'Y   d888 888b   Y8b Y888P         d8b Y8b     d888  'Y  888 ,'Y  Y88b Y8 P'  888  'Y ",
    "C8888 eeee C8888 8888D   Y8b Y8P   888   d888b Y8b   C8888 eeee 888C8   b Y88b Y     888     ",
    ' Y888 888P  Y888 888P     Y8b Y         d888888888b   Y888 888P 888 ",d 8b Y88b      888     ',
    '  "88 88"    "88 88"       Y8P         d8888888b Y8b   "88 88"  888,d88 88b Y88b     888     ',
]




def detect_repo_version() -> str:
    env_version = os.environ.get('GOV_AGENTIC_AI_VERSION')
    if env_version:
        return env_version
    try:
        result = subprocess.run(
            ['git', 'describe', '--tags', '--always'],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        version = result.stdout.strip()
        if version:
            return version
    except Exception:
        pass
    return 'unknown-version'


def render_brand_header() -> None:
    palette = [ANSI_CYAN, ANSI_BLUE, ANSI_MAGENTA, ANSI_CYAN, ANSI_BLUE, ANSI_MAGENTA, ANSI_CYAN, ANSI_BLUE, ANSI_MAGENTA, ANSI_CYAN, ANSI_BLUE]
    version = detect_repo_version()
    print(f'{ANSI_BOLD}Gov-Agentic AI Installer{ANSI_RESET}')
    print(f'{ANSI_DIM}Release: {version}{ANSI_RESET}')
    print()
    for idx, line in enumerate(GOV_AGENT_ASCII):
        color = palette[idx % len(palette)]
        print(f'{color}{line}{ANSI_RESET}')
    print()

CLUSTER_GROUPS = [
    ('Leadership & Governance', ['top-layer', 'bottom-gate', 'kebijakan-dan-hukum']),
    ('Operations & Administration', ['tata-usaha', 'komunikasi-dan-dokumen', 'sdm-dan-kinerja']),
    ('Planning & Execution', ['perencanaan-dan-anggaran', 'pengadaan-barang-dan-jasa']),
    ('Data & Field', ['data-dan-analitik', 'hubungan-eksternal-dan-lapangan']),
]


def ordered_clusters_with_groups(clusters: list[str]) -> list[tuple[str, str]]:
    cluster_set = set(clusters)
    ordered: list[tuple[str, str]] = []
    seen: set[str] = set()
    for group_name, group_clusters in CLUSTER_GROUPS:
        for cluster in group_clusters:
            if cluster in cluster_set and cluster not in seen:
                ordered.append((group_name, cluster))
                seen.add(cluster)
    for cluster in clusters:
        if cluster not in seen:
            ordered.append(('Other', cluster))
            seen.add(cluster)
    return ordered


def supports_arrow_ui(stream: TextIO | None = None) -> bool:
    stream = stream or sys.stdin
    return bool(hasattr(stream, 'isatty') and stream.isatty() and os.name != 'nt')


def read_key(stream: TextIO) -> str:
    try:
        import termios
        import tty
    except ImportError:
        return ''
    fd = stream.fileno()
    original = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        first = stream.read(1)
        if first == '\x1b':
            second = stream.read(1)
            third = stream.read(1)
            if second == '[':
                return {
                    'A': 'up',
                    'B': 'down',
                    'C': 'right',
                    'D': 'left',
                }.get(third, 'escape')
            return 'escape'
        if first == '\x03':
            raise KeyboardInterrupt
        if first in ('\r', '\n'):
            return 'enter'
        if first == ' ':
            return 'space'
        if first == '\x7f':
            return 'backspace'
        return first
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, original)




def render_footer(lines: list[str]) -> None:
    print()
    for line in lines:
        print(f'{ANSI_DIM}{line}{ANSI_RESET}')



def show_welcome_screen(output_path: Path, active_deployment_path: Path) -> None:
    if not supports_arrow_ui():
        return
    print(ANSI_CLEAR, end='')
    render_brand_header()
    print('This wizard prepares a runtime activation config for government agent deployment.\n')
    print('What this installer will do:')
    print(f'  - Write runtime config: {output_path}')
    print(f'  - Write deployment summary: {active_deployment_path}')
    print('  - Ask which runtime, memory mode, governance mode, and clusters you want active')
    print('')
    print('What this installer will NOT do:')
    print('  - It will not delete your repository folders')
    print('  - It will not rewrite knowledge-base content')
    print('  - It will not write into external runtime homes by default')
    print('')
    print('You stay in control during the wizard.')
    render_footer([
        'Enter = start installer',
        'q = cancel installer gracefully',
        'Ctrl+C = force stop immediately',
    ])
    while True:
        key = read_key(sys.stdin)
        if key == 'enter':
            print(ANSI_RESET, end='')
            return
        if key in {'q', 'Q'}:
            raise SystemExit('Interactive installer cancelled by user before start.')

def render_single_select(label: str, options: list[str], selected_idx: int, default: str, description_group: str | None = None) -> None:
    descriptions = OPTION_DESCRIPTIONS.get(description_group or '', {})
    print(ANSI_CLEAR, end='')
    print(label)
    print('Use ↑/↓ to move through options.\n')
    for idx, option in enumerate(options):
        prefix = '›' if idx == selected_idx else ' '
        active = ANSI_ACTIVE if idx == selected_idx else ''
        reset = ANSI_RESET if idx == selected_idx else ''
        marker = ' (default)' if option == default else ''
        detail = f' - {descriptions[option]}' if option in descriptions else ''
        print(f'{active}{prefix} {option}{marker}{detail}{reset}')
    render_footer([
        'Enter = confirm current option',
        'q = cancel installer gracefully',
        'Ctrl+C = force stop immediately',
    ])


def prompt_choice_arrow(label: str, options: list[str], default: str, description_group: str | None = None) -> str:
    selected_idx = options.index(default) if default in options else 0
    while True:
        render_single_select(label, options, selected_idx, default, description_group)
        key = read_key(sys.stdin)
        if key == 'up':
            selected_idx = (selected_idx - 1) % len(options)
        elif key == 'down':
            selected_idx = (selected_idx + 1) % len(options)
        elif key == 'enter':
            print(ANSI_RESET, end='')
            return options[selected_idx]
        elif key in {'q', 'Q'}:
            raise SystemExit('Interactive installer cancelled by user.')


def render_multi_select(label: str, options: list[str], selected: set[str], cursor: int) -> None:
    print(ANSI_CLEAR, end='')
    print(label)
    print('Grouped by deployment domain so you can scan the ecosystem before toggling.\n')
    grouped = ordered_clusters_with_groups(options)
    current_group = None
    for idx, (group_name, option) in enumerate(grouped):
        if group_name != current_group:
            if current_group is not None:
                print('')
            print(f'{group_name}:')
            current_group = group_name
        prefix = '›' if idx == cursor else ' '
        active = ANSI_ACTIVE if idx == cursor else ''
        reset = ANSI_RESET if idx == cursor else ''
        marker = 'x' if option in selected else ' '
        print(f'{active}{prefix} [{marker}] {option}{reset}')
    render_footer([
        'Space = toggle highlighted cluster | Enter = confirm selection',
        'a = select all | n = clear all',
        'q = cancel installer gracefully | Ctrl+C = force stop immediately',
    ])


def prompt_clusters_arrow(clusters: list[str], default_all: bool = True) -> list[str]:
    selected = set(clusters if default_all else [])
    ordered = [cluster for _, cluster in ordered_clusters_with_groups(clusters)]
    cursor = 0
    while True:
        render_multi_select('Cluster activation checklist', ordered, selected, cursor)
        key = read_key(sys.stdin)
        if key == 'up':
            cursor = (cursor - 1) % len(ordered)
        elif key == 'down':
            cursor = (cursor + 1) % len(ordered)
        elif key == 'space':
            cluster = ordered[cursor]
            if cluster in selected:
                selected.remove(cluster)
            else:
                selected.add(cluster)
        elif key in {'a', 'A'}:
            selected = set(ordered)
        elif key in {'n', 'N'}:
            selected = set()
        elif key == 'enter':
            if not selected:
                continue
            print(ANSI_RESET, end='')
            return [cluster for cluster in ordered if cluster in selected]
        elif key in {'q', 'Q'}:
            raise SystemExit('Interactive installer cancelled by user.')


OPTION_DESCRIPTIONS = {
    'runtime': {
        'openclaw': 'OpenClaw adapter: repo-mounted runtime using skill_manifest and active role skills.',
        'hermes': 'Hermes adapter: persistent agent identity with explicit mem9/local memory precedence.',
        'codex': 'Codex adapter: local workspace with SKILL.md capability folders and verification scripts.',
        'claude': 'Claude adapter: SKILL.md-compatible import with progressive disclosure references.',
        'antigravity': 'Antigravity adapter: generic repo-mounted agent runtime with manifest-driven routing.',
        'generic': 'Global portable mode for any runtime that can read files and runtime.generated.json.',
    },
    'memory': {
        'local': 'Full local: local knowledge-base is canonical; no external memory required.',
        'mem9': 'Full mem9: mem9 is primary memory surface; use when runtime is built around mem9 recall.',
        'hybrid': 'Hybrid: local knowledge-base is source of truth; mem9 stores preferences/session memory.',
    },
    'governance': {
        'sandbox': 'Sandbox: demo/testing mode; L4 still requires approval, L3 can be explored as draft/recommendation.',
        'production': 'Production: strict HITL, audit, and data-classification enforcement; L3 and L4 require approval.',
    },
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def prompt_choice(label: str, options: list[str], default: str, description_group: str | None = None) -> str:
    if supports_arrow_ui():
        return prompt_choice_arrow(label, options, default, description_group)
    print(f'\n{label}')
    descriptions = OPTION_DESCRIPTIONS.get(description_group or '', {})
    for option in options:
        marker = ' (default)' if option == default else ''
        detail = f' - {descriptions[option]}' if option in descriptions else ''
        print(f'  - {option}{marker}{detail}')
    raw = input('Type value, or press Enter for default: ').strip()
    if not raw:
        return default
    if raw in options:
        return raw
    matches = [option for option in options if option.startswith(raw)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f'Ambiguous choice: {raw}. Matches: {", ".join(matches)}', file=sys.stderr)
        return prompt_choice(label, options, default, description_group)
    print(f'Invalid choice: {raw}', file=sys.stderr)
    return prompt_choice(label, options, default, description_group)


def prompt_clusters(clusters: list[str], default_all: bool = True) -> list[str]:
    if supports_arrow_ui():
        return prompt_clusters_arrow(clusters, default_all)
    selected = set(clusters if default_all else [])
    print('\nCluster activation checklist')
    print('Toggle by typing a cluster name. Commands: all, none, done. Press Enter to accept current selection.')
    ordered = ordered_clusters_with_groups(clusters)
    while True:
        print('')
        current_group = None
        for group_name, cluster in ordered:
            if group_name != current_group:
                if current_group is not None:
                    print('')
                print(f'  {group_name}:')
                current_group = group_name
            marker = 'x' if cluster in selected else ' '
            print(f'    [{marker}] {cluster}')
        raw = input('Selection: ').strip()
        if not raw or raw == 'done':
            if not selected:
                print('At least one cluster must be selected.')
                continue
            return [cluster for _, cluster in ordered if cluster in selected]
        if raw == 'all':
            selected = set(clusters)
            continue
        if raw == 'none':
            selected = set()
            continue
        matches = [cluster for cluster in clusters if cluster == raw or cluster.startswith(raw)]
        if len(matches) == 1:
            cluster = matches[0]
            if cluster in selected:
                selected.remove(cluster)
            else:
                selected.add(cluster)
            continue
        if len(matches) > 1:
            print(f'Ambiguous cluster name: {raw}. Matches: {", ".join(matches)}')
            continue
        print(f'Unknown cluster: {raw}')

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


def runtime_profile(runtime: str) -> dict[str, Any]:
    profile_path = ROOT / 'runtime-adapters' / runtime / 'profile.json'
    if profile_path.exists():
        return load_json(profile_path)
    return load_json(ROOT / 'runtime-adapters' / 'generic' / 'profile.json')

def expand_candidate_path(value: str) -> str:
    expanded = value
    for key, env_value in os.environ.items():
        expanded = expanded.replace(f'${{{key}}}', env_value).replace(f'%{key}%', env_value)
    return str(Path(os.path.expanduser(expanded)))

def discover_runtime(runtime: str) -> dict[str, Any]:
    os_name = platform.system() or 'Unknown'
    home_dir = str(Path.home())
    candidate_map = RUNTIME_DISCOVERY_CANDIDATES.get(runtime, {})
    candidates = candidate_map.get(os_name, candidate_map.get('Linux', []))
    expanded = [expand_candidate_path(candidate) for candidate in candidates if candidate and 'None' not in candidate]
    existing = [path for path in expanded if Path(path).exists()]
    selected = existing[0] if existing else None
    recommended = None
    if selected:
        recommended = str(Path(selected) / 'gov-agentic-ai' / 'runtime.generated.json')
    elif runtime != 'generic' and expanded:
        recommended = str(Path(expanded[0]) / 'gov-agentic-ai' / 'runtime.generated.json')
    return {
        'os_name': os_name,
        'home_dir': home_dir,
        'status': 'found' if selected else ('not_required' if runtime == 'generic' else 'not_found'),
        'candidate_paths': expanded,
        'discovered_paths': existing,
        'selected_runtime_home': selected,
        'message': runtime_discovery_message(runtime, selected),
        'recommended_runtime_config': recommended,
    }

def runtime_discovery_message(runtime: str, selected: str | None) -> str:
    if runtime == 'generic':
        return 'Generic runtime uses repo-local config only; no external runtime home is required.'
    if selected:
        return f'{runtime} runtime home found. Repo-local config remains canonical unless copied intentionally.'
    return f'{runtime} runtime home not found. Generated repo-local config only; mount this repo or copy runtime.generated.json manually.'

def runtime_config_targets(discovery: dict[str, Any]) -> dict[str, Any]:
    return {
        'repo_local': 'configs/runtime.generated.json',
        'active_deployment': 'configs/active.deployment.yaml',
        'runtime_home_recommended': discovery.get('recommended_runtime_config'),
        'write_runtime_config_default': False,
    }

def governance_policy(governance: str) -> dict[str, Any]:
    if governance == 'production':
        return {
            'mode_summary': 'Strict production mode for real government workflow deployment.',
            'human_approval_required_for': ['L3', 'L4'],
            'audit_enforcement': 'strict',
            'data_classification_enforcement': 'strict',
            'recommended_use': 'limited production, controlled pilot, or formal workflow integration',
        }
    return {
        'mode_summary': 'Sandbox mode for demo, testing, and prompt/runtime iteration.',
        'human_approval_required_for': ['L4'],
        'audit_enforcement': 'lightweight',
        'data_classification_enforcement': 'advisory',
        'recommended_use': 'demo, internal exploration, and non-production validation',
    }

def build_config(runtime: str, memory: str, governance: str, active_clusters: list[str]) -> dict[str, Any]:
    kb = load_json(KB_MANIFEST)
    skills = load_json(SKILL_MANIFEST)
    profile = runtime_profile(runtime)
    discovery = discover_runtime(runtime)
    governance_details = governance_policy(governance)
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
        'runtime_adapter': profile,
        'adapter_name': profile.get('adapter_name', runtime),
        'adapter_profile_path': profile.get('adapter_path'),
        'runtime_paths': profile.get('runtime_paths', {}),
        'runtime_overrides': profile.get('runtime_overrides', {}),
        'runtime_discovery': discovery,
        'runtime_installation': {
            'mode': 'advisory',
            'writes_external_runtime_config': False,
            'selected_runtime_home': discovery.get('selected_runtime_home'),
        },
        'runtime_config_targets': runtime_config_targets(discovery),
        'memory_mode': memory,
        'memory_policy': memory_policy(memory),
        'governance_mode': governance,
        'governance_policy': governance_details,
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
        'human_approval_required_for': governance_details['human_approval_required_for'],
        'output_contract_required_fields': [
            'summary', 'evidence_map', 'assumptions', 'confidence_status', 'red_flags', 'human_touchpoint', 'next_step'
        ],
        'runtime_boot_sequence': [
            'read_runtime_config',
            f"load_runtime_adapter_profile:{profile.get('adapter_name', runtime)}",
            'load_system_prompt',
            'load_shared_guardrail_skill',
            'default_to_yayak_router',
            'select_only_active_roles_and_skills',
            'retrieve_active_role_and_shared_knowledge',
            f"apply_memory_policy:{memory}",
            f"apply_governance_policy:{governance}",
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

    output = (ROOT / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    active_deployment = (ROOT / args.active_deployment).resolve() if not Path(args.active_deployment).is_absolute() else Path(args.active_deployment)

    if args.defaults:
        runtime = args.runtime or defaults.get('runtime_target', 'generic')
        memory = args.memory or defaults.get('memory_mode', 'hybrid')
        governance = args.governance or defaults.get('governance_mode', 'production')
        active_clusters = parse_csv(args.clusters) or defaults.get('active_clusters') or clusters
    else:
        show_welcome_screen(output, active_deployment)
        runtime = args.runtime or prompt_choice('Runtime target', RUNTIMES, defaults.get('runtime_target', 'generic'), 'runtime')
        memory = args.memory or prompt_choice('Memory mode', MEMORY_MODES, defaults.get('memory_mode', 'hybrid'), 'memory')
        active_clusters = parse_csv(args.clusters) or prompt_clusters(clusters)
        governance = args.governance or prompt_choice('Governance mode', GOVERNANCE_MODES, defaults.get('governance_mode', 'production'), 'governance')

    unknown = sorted(set(active_clusters) - set(clusters))
    if unknown:
        raise SystemExit(f'Unknown clusters: {", ".join(unknown)}')

    config = build_config(runtime, memory, governance, active_clusters)
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
    print(f'adapter_profile={config.get("adapter_profile_path")}')
    discovery = config.get('runtime_discovery', {})
    print(f'runtime_discovery={discovery.get("status")}: {discovery.get("message")}')
    target = config.get('runtime_config_targets', {}).get('runtime_home_recommended')
    if target:
        print(f'runtime_config_recommended={target}')
    print(f'governance_summary={config.get("governance_policy", {}).get("mode_summary")}')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInstaller force-stopped by user.', file=sys.stderr)
        raise SystemExit(130)
