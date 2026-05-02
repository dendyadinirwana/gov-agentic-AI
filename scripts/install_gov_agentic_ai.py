#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO

ROOT = Path(__file__).resolve().parents[1]
KB_MANIFEST = ROOT / 'knowledge-base' / 'kb_manifest.json'
SKILL_MANIFEST = ROOT / 'skills' / 'skill_manifest.json'
DEFAULTS_PATH = ROOT / 'configs' / 'installer.defaults.json'
DEFAULT_OUTPUT = ROOT / 'configs' / 'runtime.generated.json'
DEFAULT_ACTIVE_DEPLOYMENT = ROOT / 'configs' / 'active.deployment.yaml'
DEFAULT_PACK_ROOT = ROOT / 'build' / 'runtime-pack'
DEFAULT_CENTRAL_HOME = Path.home() / '.gov-agentic-ai'
MANAGED_SUBTREE = 'gov-agentic-ai'
SHIM_SKILL_NAMES = {'gov-gov-ai-yayak', 'gov-agentic-common'}

RUNTIMES = ['openclaw', 'hermes', 'codex', 'claude', 'antigravity', 'generic']
MEMORY_MODES = ['local', 'mem9', 'hybrid']
GOVERNANCE_MODES = ['sandbox', 'production']
INSTALL_ACTIONS = ['local_only', 'apply_install', 'back', 'cancel']

CENTRAL_HOME_CANDIDATES = {'Darwin': ['~/.gov-agentic-ai'], 'Linux': ['~/.gov-agentic-ai'], 'Windows': ['%USERPROFILE%/.gov-agentic-ai']}

RUNTIME_DISCOVERY_CANDIDATES = {
    'generic': {'Darwin': ['~/.agents/skills'], 'Linux': ['~/.agents/skills'], 'Windows': ['%USERPROFILE%/.agents/skills']},
    'hermes': {'Darwin': ['~/.hermes'], 'Linux': ['~/.hermes'], 'Windows': ['%USERPROFILE%/.hermes']},
    'openclaw': {'Darwin': ['~/.openclaw'], 'Linux': ['~/.openclaw'], 'Windows': ['%USERPROFILE%/.openclaw']},
    'codex': {'Darwin': ['~/.codex'], 'Linux': ['~/.codex'], 'Windows': ['%USERPROFILE%/.codex']},
    'claude': {'Darwin': ['~/.claude'], 'Linux': ['~/.claude'], 'Windows': ['%USERPROFILE%/.claude']},
    'antigravity': {'Darwin': ['~/.antigravity'], 'Linux': ['~/.antigravity'], 'Windows': ['%USERPROFILE%/.antigravity']},
}

ANSI_CLEAR = '\033[2J\033[H'
ANSI_RESET = '\033[0m'
ANSI_ACTIVE = '\033[7m'
ANSI_DIM = '\033[2m'
ANSI_CYAN = '\033[96m'
ANSI_BLUE = '\033[94m'
ANSI_MAGENTA = '\033[95m'
ANSI_BOLD = '\033[1m'
ANSI_GREEN = '\033[92m'
ANSI_YELLOW = '\033[93m'
ANSI_RED = '\033[91m'

GOV_AGENT_ASCII = [
    "  e88'Y88    e88 88e   Y8b Y88888P         e Y8b       e88'Y88  888'Y88 Y88b Y88 88P'888'Y88 ",
    " d888  'Y   d888 888b   Y8b Y888P         d8b Y8b     d888  'Y  888 ,'Y  Y88b Y8 P'  888  'Y ",
    "C8888 eeee C8888 8888D   Y8b Y8P   888   d888b Y8b   C8888 eeee 888C8   b Y88b Y     888     ",
    ' Y888 888P  Y888 888P     Y8b Y         d888888888b   Y888 888P 888 ",d 8b Y88b      888     ',
    '  "88 88"    "88 88"       Y8P         d8888888b Y8b   "88 88"  888,d88 88b Y88b     888     ',
]

CLUSTER_GROUPS = [
    ('Leadership & Governance', ['top-layer', 'bottom-gate', 'kebijakan-dan-hukum']),
    ('Operations & Administration', ['tata-usaha', 'komunikasi-dan-dokumen', 'sdm-dan-kinerja']),
    ('Planning & Execution', ['perencanaan-dan-anggaran', 'pengadaan-barang-dan-jasa']),
    ('Data & Field', ['data-dan-analitik', 'hubungan-eksternal-dan-lapangan']),
]

OPTION_DESCRIPTIONS = {
    'runtime': {
        'openclaw': 'OpenClaw adapter: repo-mounted runtime using skill_manifest and active role skills.',
        'hermes': 'Hermes adapter: persistent agent identity with explicit mem9/local memory precedence.',
        'codex': 'Codex adapter: local workspace with SKILL.md capability folders and verification scripts.',
        'claude': 'Claude adapter: SKILL.md-compatible import with progressive disclosure references.',
        'antigravity': 'Antigravity adapter: generic repo-mounted agent runtime with manifest-driven routing.',
        'generic': 'Global portable mode for agent skills at ~/.agents/skills with runtime pack metadata.',
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


def display_path(value: str | Path | None, max_len: int = 72) -> str:
    if value is None:
        return '-'
    text = str(value)
    home = str(Path.home())
    if text.startswith(home):
        text = '~' + text[len(home):]
    if len(text) <= max_len:
        return text
    keep = max_len - 3
    left = keep // 2
    right = keep - left
    return f'{text[:left]}...{text[-right:]}'


def render_brand_header() -> None:
    palette = [ANSI_CYAN, ANSI_BLUE, ANSI_MAGENTA, ANSI_CYAN, ANSI_BLUE]
    version = detect_repo_version()
    print(f'{ANSI_BOLD}Gov-Agentic AI Installer{ANSI_RESET}')
    print(f'{ANSI_DIM}Release: {version}{ANSI_RESET}')
    print()
    for idx, line in enumerate(GOV_AGENT_ASCII):
        print(f'{palette[idx % len(palette)]}{line}{ANSI_RESET}')
    print()


def render_mini_header(title: str, subtitle: str | None = None) -> None:
    print(f'{ANSI_BOLD}{title}{ANSI_RESET}')
    print(f'{ANSI_DIM}Release: {detect_repo_version()}{ANSI_RESET}')
    if subtitle:
        print(f'{ANSI_DIM}{subtitle}{ANSI_RESET}')
    print()


def print_section(title: str) -> None:
    print(f'{ANSI_BOLD}{title}{ANSI_RESET}')


def render_footer(lines: list[str]) -> None:
    print()
    for line in lines:
        print(f'{ANSI_DIM}{line}{ANSI_RESET}')


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


def cluster_group_summary(active_clusters: list[str]) -> list[tuple[str, list[str]]]:
    grouped: list[tuple[str, list[str]]] = []
    current_group = None
    current_items: list[str] = []
    for group_name, cluster in ordered_clusters_with_groups(active_clusters):
        if group_name != current_group:
            if current_group is not None:
                grouped.append((current_group, current_items))
            current_group = group_name
            current_items = [cluster]
        else:
            current_items.append(cluster)
    if current_group is not None:
        grouped.append((current_group, current_items))
    return grouped


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
                return {'A': 'up', 'B': 'down', 'C': 'right', 'D': 'left'}.get(third, 'escape')
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


def discover_central_home() -> dict[str, Any]:
    os_name = platform.system() or 'Unknown'
    candidates = CENTRAL_HOME_CANDIDATES.get(os_name, CENTRAL_HOME_CANDIDATES.get('Linux', []))
    expanded = [expand_candidate_path(candidate) for candidate in candidates]
    existing = [path for path in expanded if Path(path).exists()]
    selected = existing[0] if existing else (expanded[0] if expanded else str(DEFAULT_CENTRAL_HOME))
    return {
        'os_name': os_name,
        'candidate_paths': expanded,
        'discovered_paths': existing,
        'status': 'found' if existing else 'not_found',
        'central_home_root': selected,
        'message': 'Central canonical home found.' if existing else 'Central canonical home will be created on install.',
    }


def central_pack_root_for(output: Path | None = None) -> Path:
    version = detect_repo_version().replace('/', '-').replace(' ', '-')
    if output and output.is_absolute() and not output.is_relative_to(ROOT):
        return output.parent / 'central-home-pack' / version
    return ROOT / 'build' / 'central-home' / version


def shim_pack_root_for(runtime: str, output: Path | None = None) -> Path:
    version = detect_repo_version().replace('/', '-').replace(' ', '-')
    if output and output.is_absolute() and not output.is_relative_to(ROOT):
        return output.parent / 'runtime-shim' / runtime
    return DEFAULT_PACK_ROOT / runtime / version


def discover_runtime(runtime: str) -> dict[str, Any]:
    os_name = platform.system() or 'Unknown'
    home_dir = str(Path.home())
    profile = runtime_profile(runtime)
    candidate_map = RUNTIME_DISCOVERY_CANDIDATES.get(runtime, {})
    candidates = candidate_map.get(os_name, candidate_map.get('Linux', []))
    expanded = [expand_candidate_path(candidate) for candidate in candidates if candidate and 'None' not in candidate]
    existing = [path for path in expanded if Path(path).exists()]
    selected = existing[0] if existing else None
    canonical_home = selected or (expanded[0] if expanded else None)
    install_root = str(Path(canonical_home) / MANAGED_SUBTREE) if canonical_home else None
    install_type = 'global-surface' if runtime == 'generic' else 'runtime-home'
    runtime_config_target = str(Path(install_root) / 'runtime.generated.json') if install_root else None
    skill_target = str(Path(install_root) / 'skills') if install_root else None
    central = discover_central_home()
    return {
        'os_name': os_name,
        'home_dir': home_dir,
        'status': 'found' if selected else 'not_found',
        'candidate_paths': expanded,
        'discovered_paths': existing,
        'selected_runtime_home': selected,
        'canonical_runtime_home': canonical_home,
        'install_target_root': install_root,
        'install_target_type': install_type,
        'recommended_runtime_config': runtime_config_target,
        'recommended_skill_home': skill_target if runtime == 'generic' else None,
        'message': runtime_discovery_message(runtime, selected),
        'profile_summary': profile.get('description', ''),
        'recommended': runtime != 'generic' and selected is not None,
        'central_home_root': central.get('central_home_root'),
        'central_home_status': central.get('status'),
        'central_home_message': central.get('message'),
    }


def runtime_discovery_message(runtime: str, selected: str | None) -> str:
    if runtime == 'generic':
        if selected:
            return 'Generic agent skill home found. Repo-local config remains canonical unless copied intentionally.'
        return 'Generic agent skill home not found. Generated repo-local config only; copy skills into ~/.agents/skills if needed.'
    if selected:
        return f'{runtime} runtime home found. Repo-local config remains canonical unless copied intentionally.'
    return f'{runtime} runtime home not found. Generated repo-local config only; mount this repo or copy runtime.generated.json manually.'


def scan_runtime_targets(runtimes: list[str]) -> dict[str, dict[str, Any]]:
    return {runtime: discover_runtime(runtime) for runtime in runtimes}


def order_runtime_options(runtimes: list[str], scan_map: dict[str, dict[str, Any]]) -> list[str]:
    detected = [runtime for runtime in runtimes if scan_map.get(runtime, {}).get('status') == 'found' and runtime != 'generic']
    generic = [runtime for runtime in runtimes if runtime == 'generic']
    missing = [runtime for runtime in runtimes if runtime not in detected and runtime not in generic]
    return detected + generic + missing


def runtime_option_label(runtime: str, scan_map: dict[str, dict[str, Any]] | None = None) -> str:
    if not scan_map:
        return runtime
    status = scan_map.get(runtime, {}).get('status')
    badge = 'DETECTED' if status == 'found' else 'NOT FOUND'
    return f'{runtime} [{badge}]'


def runtime_config_targets(discovery: dict[str, Any], output: Path, active_deployment: Path, shim_pack_root: Path, central_pack_root: Path) -> dict[str, Any]:
    return {
        'repo_local': str(output.relative_to(ROOT) if output.is_relative_to(ROOT) else output),
        'active_deployment': str(active_deployment.relative_to(ROOT) if active_deployment.is_relative_to(ROOT) else active_deployment),
        'runtime_pack_root': str(shim_pack_root.relative_to(ROOT) if shim_pack_root.is_relative_to(ROOT) else shim_pack_root),
        'central_pack_root': str(central_pack_root.relative_to(ROOT) if central_pack_root.is_relative_to(ROOT) else central_pack_root),
        'runtime_home_recommended': discovery.get('recommended_runtime_config'),
        'runtime_skill_home_recommended': discovery.get('recommended_skill_home'),
        'write_runtime_config_default': False,
    }


def runtime_pack_root_for(runtime: str, output: Path | None = None) -> Path:
    version = detect_repo_version().replace('/', '-').replace(' ', '-')
    base = DEFAULT_PACK_ROOT / runtime / version
    if output and output.is_absolute() and not output.is_relative_to(ROOT):
        return output.parent / 'runtime-pack' / runtime
    return base


def current_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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


def memory_policy(memory: str) -> dict[str, str]:
    if memory == 'local':
        return {'canonical_knowledge': 'local knowledge-base only', 'working_memory': 'runtime-local only', 'external_memory': 'disabled'}
    if memory == 'mem9':
        return {'canonical_knowledge': 'mem9 primary memory surface', 'working_memory': 'mem9 session and preference memory', 'external_memory': 'mem9 required'}
    return {
        'canonical_knowledge': 'local knowledge-base is source of truth',
        'working_memory': 'mem9 stores preferences, session memory, and operational recall',
        'external_memory': 'mem9 optional but recommended',
    }


def relative_to_root(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def build_config(runtime: str, memory: str, governance: str, active_clusters: list[str], output: Path, active_deployment: Path, install_mode: str = 'copy', install_applied: bool = False, install_target_root: str | None = None, pack_root: Path | None = None, central_home_root: str | None = None, central_pack_root: Path | None = None) -> dict[str, Any]:
    kb = load_json(KB_MANIFEST)
    skills = load_json(SKILL_MANIFEST)
    profile = runtime_profile(runtime)
    discovery = discover_runtime(runtime)
    governance_details = governance_policy(governance)
    central_home = central_home_root or discovery.get('central_home_root') or str(DEFAULT_CENTRAL_HOME)
    shim_pack = pack_root or shim_pack_root_for(runtime, output)
    central_pack = central_pack_root or central_pack_root_for(output)
    role_rows = kb['roles']
    skill_by_role = {(s['cluster'], s['role'], s['alias']): s for s in skills['skills']}
    active_roles = []
    active_skills = []
    for role in role_rows:
        if role['cluster'] not in active_clusters:
            continue
        skill = skill_by_role[(role['cluster'], role['role'], role['alias'])]
        active_roles.append({'cluster': role['cluster'], 'role': role['role'], 'alias': role['alias'], 'knowledge_path': str(Path(kb['base_path']) / role['path']), 'skill_name': skill['name'], 'skill_path': skill['skill_path'], 'prompt_path': skill['prompt_path']})
        active_skills.append({'name': skill['name'], 'skill_path': skill['skill_path'], 'skill_md': skill['skill_md'], 'role': skill['role'], 'alias': skill['alias'], 'cluster': skill['cluster']})
    install_target_root = install_target_root or discovery.get('install_target_root')
    install_target_config = str(Path(install_target_root) / 'runtime.generated.json') if install_target_root else None
    install_target_skills = str(Path(install_target_root) / 'skills') if install_target_root else None
    config = {
        'project_name': 'gov-agentic-ai',
        'project_version': detect_repo_version(),
        'runtime_target': runtime,
        'runtime_adapter': profile,
        'adapter_name': profile.get('adapter_name', runtime),
        'adapter_profile_path': profile.get('adapter_path'),
        'runtime_paths': profile.get('runtime_paths', {}),
        'runtime_overrides': profile.get('runtime_overrides', {}),
        'runtime_discovery': discovery,
        'runtime_installation': {'mode': install_mode, 'writes_external_runtime_config': install_mode == 'copy', 'selected_runtime_home': discovery.get('selected_runtime_home'), 'install_applied': install_applied, 'installed_at': current_timestamp() if install_applied else None},
        'memory_mode': memory,
        'memory_policy': memory_policy(memory),
        'governance_mode': governance,
        'governance_policy': governance_details,
        'agent_entrypoint': 'AGENT_README.md',
        'runtime_handshake': 'runtime-adapters/universal/RUNTIME_HANDSHAKE.md',
        'bootstrap_example': 'examples/BOOTSTRAP_EXAMPLE.json',
        'system_prompt': 'prompts/system/YayakAI_Master_System_Prompt_v3.0.md',
        'default_router_role': 'GOV-AI',
        'default_router_alias': 'Yayak',
        'default_router_skill': 'gov-gov-ai-yayak',
        'shared_guardrail_skill': skills['shared_skill'],
        'government_work_logic': 'docs/architecture/GOVERNMENT_WORK_LOGIC.md',
        'authority_matrix': 'configs/authority_matrix.json',
        'decision_engine_entrypoint': 'scripts/government_decision_engine.py',
        'decision_engine': {'enabled': True, 'entrypoint': 'scripts/government_decision_engine.py', 'workflow_schema': 'schemas/government_workflow_state.schema.json', 'authority_matrix': 'configs/authority_matrix.json', 'rules_config': 'configs/government_logic_rules.json', 'default_mode': 'gating' if governance == 'production' else 'advisory'},
        'audit_schema': 'schemas/audit_log_template_v3.0.json',
        'acceptance_tests': 'schemas/Gov_Agentic_AI_v3.1_Acceptance_Tests.json',
        'knowledge_base_root': kb['base_path'],
        'shared_knowledge_root': 'knowledge-base/_shared',
        'active_clusters': active_clusters,
        'active_roles': active_roles,
        'active_skills': active_skills,
        'human_approval_required_for': governance_details['human_approval_required_for'],
        'output_contract_required_fields': ['summary', 'evidence_map', 'assumptions', 'confidence_status', 'red_flags', 'human_touchpoint', 'next_step'],
        'runtime_boot_sequence': ['read_local_runtime_shim_config', 'resolve_central_home_root', 'read_agent_entrypoint_contract', 'read_canonical_runtime_config', f'load_runtime_adapter_profile:{profile.get("adapter_name", runtime)}', 'load_local_yayak_bootstrap', 'load_shared_guardrail_skill', 'load_government_work_logic', 'initialize_decision_engine', 'default_to_yayak_router', 'route_deeper_role_loading_to_central_home', f'apply_memory_policy:{memory}', f'governance_mode:{governance}'],
        'runtime_pack_root': relative_to_root(shim_pack),
        'central_pack_root': relative_to_root(central_pack),
        'install_target_root': install_target_root,
        'install_target_config': install_target_config,
        'install_target_skills': install_target_skills,
        'install_target_type': discovery.get('install_target_type'),
        'install_mode': install_mode,
        'install_applied': install_applied,
        'installed_at': current_timestamp() if install_applied else None,
        'central_home_root': central_home,
        'runtime_shim_root': install_target_root,
        'runtime_attach_mode': 'thin-shim',
        'canonical_repo_root': central_home,
        'shim_installed_skills': ['gov-gov-ai-yayak', 'gov-agentic-common'],
        'canonical_skill_manifest': str(Path(central_home) / 'skills' / 'skill_manifest.json'),
        'canonical_knowledge_root': str(Path(central_home) / 'knowledge-base'),
        'canonical_system_prompt': str(Path(central_home) / 'prompts' / 'system' / 'YayakAI_Master_System_Prompt_v3.0.md'),
        'canonical_agent_entrypoint': str(Path(central_home) / 'AGENT_README.md'),
        'canonical_runtime_config': str(Path(central_home) / 'configs' / 'runtime.generated.json'),
    }
    config['runtime_config_targets'] = runtime_config_targets(discovery, output, active_deployment, shim_pack, central_pack)
    return config


def status_color(status: str) -> str:
    if status in {'found', 'detected', 'recommended'}:
        return ANSI_GREEN
    if status in {'global-surface'}:
        return ANSI_YELLOW
    return ANSI_RED


def render_runtime_scan_summary(scan_map: dict[str, dict[str, Any]]) -> None:
    print('Detected runtime homes on this machine:')
    for runtime in RUNTIMES:
        info = scan_map[runtime]
        status = info.get('status')
        icon = '✓' if status == 'found' else '·'
        target = info.get('selected_runtime_home') or info.get('canonical_runtime_home')
        label = 'detected' if status == 'found' else 'not found'
        preferred = ' (recommended)' if runtime != 'generic' and status == 'found' else ''
        color = status_color(status)
        print(f'  {color}{icon}{ANSI_RESET} {runtime:<12} {label:<10} {display_path(target)}{preferred}')
    print('')


def show_welcome_screen(output_path: Path, active_deployment_path: Path, runtime_scan: dict[str, dict[str, Any]]) -> None:
    if not supports_arrow_ui():
        return
    print(ANSI_CLEAR, end='')
    render_brand_header()
    print('This wizard prepares a runtime activation config and optional runtime-home install for government agent deployment.\n')
    print('What this installer will do:')
    print(f'  - Write repo-local runtime config: {display_path(output_path)}')
    print(f'  - Write deployment summary: {display_path(active_deployment_path)}')
    print('  - Generate a runtime pack for the selected target')
    print('  - Optionally install that pack into the canonical runtime home')
    print('')
    print('What this installer will NOT do:')
    print('  - It will not delete your repository folders')
    print('  - It will not rewrite knowledge-base content')
    print('  - It will not touch files outside the managed gov-agentic-ai subtree')
    print('')
    render_runtime_scan_summary(runtime_scan)
    print('You stay in control during the wizard.')
    render_footer(['Enter = start installer', 'q = cancel installer gracefully', 'Ctrl+C = force stop immediately'])
    while True:
        key = read_key(sys.stdin)
        if key == 'enter':
            print(ANSI_RESET, end='')
            return
        if key in {'q', 'Q'}:
            raise SystemExit('Interactive installer cancelled by user before start.')


def render_single_select(label: str, options: list[str], selected_idx: int, default: str, description_group: str | None = None, scan_map: dict[str, dict[str, Any]] | None = None) -> None:
    descriptions = OPTION_DESCRIPTIONS.get(description_group or '', {})
    print(ANSI_CLEAR, end='')
    render_mini_header(label)
    for idx, option in enumerate(options):
        prefix = '›' if idx == selected_idx else ' '
        active = ANSI_ACTIVE if idx == selected_idx else ''
        reset = ANSI_RESET if idx == selected_idx else ''
        marker = ' (default)' if option == default else ''
        detail = f' - {descriptions[option]}' if option in descriptions else ''
        show_label = runtime_option_label(option, scan_map) if description_group == 'runtime' else option
        print(f'{active}{prefix} {show_label}{marker}{detail}{reset}')
    render_footer(['Enter = confirm current option', 'q = cancel installer gracefully', 'Ctrl+C = force stop immediately'])


def prompt_choice_arrow(label: str, options: list[str], default: str, description_group: str | None = None, scan_map: dict[str, dict[str, Any]] | None = None) -> str:
    selected_idx = options.index(default) if default in options else 0
    while True:
        render_single_select(label, options, selected_idx, default, description_group, scan_map)
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
    render_mini_header(label, 'Grouped by deployment domain so you can scan the ecosystem before toggling.')
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
    render_footer(['Space = toggle highlighted cluster | Enter = confirm selection', 'a = select all | n = clear all', 'q = cancel installer gracefully | Ctrl+C = force stop immediately'])


def prompt_clusters_arrow(clusters: list[str], default_all: bool = True, preselected: list[str] | None = None) -> list[str]:
    selected = set(preselected if preselected is not None else (clusters if default_all else []))
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


def prompt_choice(label: str, options: list[str], default: str, description_group: str | None = None, scan_map: dict[str, dict[str, Any]] | None = None) -> str:
    if supports_arrow_ui():
        return prompt_choice_arrow(label, options, default, description_group, scan_map)
    print(f'\n{label}')
    descriptions = OPTION_DESCRIPTIONS.get(description_group or '', {})
    for option in options:
        marker = ' (default)' if option == default else ''
        detail = f' - {descriptions[option]}' if option in descriptions else ''
        show_label = runtime_option_label(option, scan_map) if description_group == 'runtime' else option
        print(f'  - {show_label}{marker}{detail}')
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
        return prompt_choice(label, options, default, description_group, scan_map)
    print(f'Invalid choice: {raw}', file=sys.stderr)
    return prompt_choice(label, options, default, description_group, scan_map)


def prompt_clusters(clusters: list[str], default_all: bool = True, preselected: list[str] | None = None) -> list[str]:
    if supports_arrow_ui():
        return prompt_clusters_arrow(clusters, default_all, preselected)
    selected = set(preselected if preselected is not None else (clusters if default_all else []))
    ordered = ordered_clusters_with_groups(clusters)
    print('\nCluster activation checklist')
    print('Toggle by typing a cluster name. Commands: all, none, done. Press Enter to accept current selection.')
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
            selected = {cluster for _, cluster in ordered}
            continue
        if raw == 'none':
            selected = set()
            continue
        matches = [cluster for _, cluster in ordered if cluster == raw or cluster.startswith(raw)]
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


def parse_csv(value: str | None) -> list[str] | None:
    if value is None:
        return None
    return [part.strip() for part in value.split(',') if part.strip()]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def collect_pack_checksums(pack_root: Path) -> dict[str, str]:
    return {str(path.relative_to(pack_root)): file_sha256(path) for path in sorted(pack_root.rglob('*')) if path.is_file()}


def install_receipt_payload(config: dict[str, Any], target_root: Path, installed_file_count: int, install_kind: str) -> dict[str, Any]:
    return {
        'project_name': config['project_name'],
        'project_version': config['project_version'],
        'runtime_target': config['runtime_target'],
        'install_kind': install_kind,
        'install_target_root': str(target_root),
        'install_target_type': config['install_target_type'],
        'install_mode': config['install_mode'],
        'installed_at': current_timestamp(),
        'agent_entrypoint': config['agent_entrypoint'],
        'runtime_config': 'runtime.generated.json',
        'managed_subtree': target_root.name,
        'active_cluster_count': len(config['active_clusters']),
        'active_role_count': len(config['active_roles']),
        'active_skill_count': len(config['active_skills']),
        'installed_file_count': installed_file_count,
        'central_home_root': config['central_home_root'],
        'runtime_attach_mode': config['runtime_attach_mode'],
    }


def copy_path(src: Path, dst: Path) -> None:
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True, symlinks=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def write_yaml_like(path: Path, config: dict[str, Any]) -> None:
    lines = [
        f"project_name: {config['project_name']}",
        f"project_version: {config['project_version']}",
        f"runtime_target: {config['runtime_target']}",
        f"memory_mode: {config['memory_mode']}",
        f"governance_mode: {config['governance_mode']}",
        f"central_home_root: {config['central_home_root']}",
        f"runtime_shim_root: {config['runtime_shim_root']}",
        f"runtime_pack_root: {config['runtime_pack_root']}",
        f"central_pack_root: {config['central_pack_root']}",
        'human_approval_required_for:',
    ]
    lines.extend(f"  - {item}" for item in config['human_approval_required_for'])
    lines.append('active_clusters:')
    lines.extend(f"  - {item}" for item in config['active_clusters'])
    lines.append(f"active_role_count: {len(config['active_roles'])}")
    lines.append(f"active_skill_count: {len(config['active_skills'])}")
    path.write_text('\n'.join(lines) + '\n')


def generate_pack_manifest(config: dict[str, Any], pack_kind: str) -> dict[str, Any]:
    return {
        'project_name': config['project_name'],
        'project_version': config['project_version'],
        'runtime_target': config['runtime_target'],
        'pack_kind': pack_kind,
        'generated_at': current_timestamp(),
        'agent_entrypoint': config['agent_entrypoint'],
        'handshake_doc': 'runtime-adapters/universal/RUNTIME_HANDSHAKE.md',
        'bootstrap_example': 'examples/BOOTSTRAP_EXAMPLE.json',
        'active_clusters': config['active_clusters'],
        'active_skill_names': [skill['name'] for skill in config['active_skills']],
        'install_target_type': config['install_target_type'],
        'central_home_root': config['central_home_root'],
        'runtime_attach_mode': config['runtime_attach_mode'],
    }


def central_home_copy_list() -> list[Path]:
    return [
        Path('AGENT_README.md'), Path('README.md'), Path('INSTALL.md'), Path('docs'), Path('examples'),
        Path('knowledge-base'), Path('prompts'), Path('runtime-adapters'), Path('schemas'), Path('scripts'),
        Path('skills'), Path('configs/government_logic_rules.json'), Path('configs/authority_matrix.json')
    ]


def build_central_home_pack(config: dict[str, Any]) -> dict[str, Any]:
    pack_root = ROOT / config['central_pack_root'] if not Path(config['central_pack_root']).is_absolute() else Path(config['central_pack_root'])
    if pack_root.exists():
        shutil.rmtree(pack_root)
    pack_root.mkdir(parents=True, exist_ok=True)
    for rel in central_home_copy_list():
        copy_path(ROOT / rel, pack_root / rel)
    central_config = json.loads(json.dumps(config))
    central_config['central_pack_root'] = '.'
    (pack_root / 'configs').mkdir(parents=True, exist_ok=True)
    (pack_root / 'configs' / 'runtime.generated.json').write_text(json.dumps(central_config, ensure_ascii=False, indent=2) + '\n')
    manifest = generate_pack_manifest(config, 'central-home')
    manifest['checksums'] = collect_pack_checksums(pack_root)
    (pack_root / 'central-home.manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return {'pack_root': str(pack_root), 'config_path': str(pack_root / 'configs' / 'runtime.generated.json'), 'manifest_path': str(pack_root / 'central-home.manifest.json')}


def build_runtime_pack(config: dict[str, Any], output: Path, active_deployment: Path) -> dict[str, Any]:
    pack_root = ROOT / config['runtime_pack_root'] if not Path(config['runtime_pack_root']).is_absolute() else Path(config['runtime_pack_root'])
    if pack_root.exists():
        shutil.rmtree(pack_root)
    pack_root.mkdir(parents=True, exist_ok=True)
    files_to_copy = [
        Path(config['agent_entrypoint']), Path(config['runtime_handshake']), Path(config['bootstrap_example']),
        Path(config['system_prompt']), Path(config['shared_guardrail_skill']), Path(config['government_work_logic']),
        Path(config['authority_matrix']), Path(config['decision_engine_entrypoint']), Path(config['decision_engine']['workflow_schema']),
        Path(config['decision_engine']['rules_config']), Path(config['audit_schema']), Path(config['acceptance_tests']),
        Path(config['adapter_profile_path']), Path('skills/roles/top-layer__gov-ai_yayak'), Path('prompts/roles/top-layer__gov-ai_yayak.md')
    ]
    for adapter_doc in config.get('runtime_adapter', {}).get('adapter_docs', []):
        files_to_copy.append(Path(adapter_doc))
    seen=set()
    for rel in files_to_copy:
        s=str(rel)
        if s in seen:
            continue
        seen.add(s)
        copy_path(ROOT / rel, pack_root / rel)
    link_payload = {
        'central_home_root': config['central_home_root'],
        'canonical_skill_manifest': config['canonical_skill_manifest'],
        'canonical_knowledge_root': config['canonical_knowledge_root'],
        'canonical_system_prompt': config['canonical_system_prompt'],
        'canonical_agent_entrypoint': config['canonical_agent_entrypoint'],
        'canonical_runtime_config': config['canonical_runtime_config'],
        'runtime_attach_mode': config['runtime_attach_mode'],
        'shim_installed_skills': config['shim_installed_skills'],
    }
    pack_config = json.loads(json.dumps(config))
    pack_config['runtime_pack_root'] = '.'
    pack_config_path = pack_root / 'runtime.generated.json'
    pack_deployment_path = pack_root / 'active.deployment.yaml'
    pack_adapter_path = pack_root / 'runtime-adapter.profile.json'
    pack_skills_manifest = pack_root / 'active-skills.json'
    pack_manifest_path = pack_root / 'runtime-pack.manifest.json'
    pack_link_path = pack_root / 'runtime-link.json'
    subset_skills = [skill for skill in config['active_skills'] if skill['name'] in SHIM_SKILL_NAMES]
    pack_config_path.write_text(json.dumps(pack_config, ensure_ascii=False, indent=2) + '\n')
    pack_deployment_path.write_text(active_deployment.read_text())
    pack_adapter_path.write_text(json.dumps(config['runtime_adapter'], ensure_ascii=False, indent=2) + '\n')
    pack_skills_manifest.write_text(json.dumps({'skills': subset_skills}, ensure_ascii=False, indent=2) + '\n')
    pack_link_path.write_text(json.dumps(link_payload, ensure_ascii=False, indent=2) + '\n')
    manifest = generate_pack_manifest(config, 'runtime-shim')
    manifest['checksums'] = collect_pack_checksums(pack_root)
    pack_manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return {'pack_root': str(pack_root), 'config_path': str(pack_config_path), 'deployment_path': str(pack_deployment_path), 'adapter_profile_path': str(pack_adapter_path), 'skills_manifest_path': str(pack_skills_manifest), 'manifest_path': str(pack_manifest_path), 'link_path': str(pack_link_path)}


def summarize_tree(root: Path, max_items: int = 18) -> list[str]:
    if not root.exists():
        return ['(empty)']
    items: list[str] = []
    for child in sorted(root.rglob('*')):
        rel = child.relative_to(root)
        prefix = '[D]' if child.is_dir() else '[F]'
        items.append(f'{prefix} {rel}')
        if len(items) >= max_items:
            break
    total = sum(1 for _ in root.rglob('*'))
    if total > max_items:
        items.append(f'... and {total - max_items} more entries')
    return items or ['(empty)']


def collect_install_existing_summary(target_root: Path) -> dict[str, Any]:
    if not target_root.exists():
        return {'target_exists': False, 'existing_file_count': 0, 'existing_tree_preview': ['(target does not exist yet)']}
    existing_files = sum(1 for path in target_root.rglob('*') if path.is_file())
    return {'target_exists': True, 'existing_file_count': existing_files, 'existing_tree_preview': summarize_tree(target_root, 12)}


def pack_preview_summary(pack_root: Path) -> dict[str, Any]:
    return {
        'pack_file_count': sum(1 for path in pack_root.rglob('*') if path.is_file()) if pack_root.exists() else 0,
        'pack_tree_preview': summarize_tree(pack_root, 14),
    }


def render_cluster_summary(active_clusters: list[str]) -> None:
    for group_name, items in cluster_group_summary(active_clusters):
        compact = ', '.join(items)
        print(f'  {group_name} [{len(items)}]')
        print(f'    {compact}')


def review_selections(runtime: str, memory: str, governance: str, active_clusters: list[str], output_path: Path, active_deployment_path: Path, discovery: dict[str, Any], pack_root: Path, install_summary: dict[str, Any], pack_summary: dict[str, Any]) -> str:
    if not supports_arrow_ui():
        return 'apply_install'
    options = INSTALL_ACTIONS
    cursor = 1
    while True:
        print(ANSI_CLEAR, end='')
        render_mini_header('Review Deployment Setup', 'Final check before any files are written.')
        print_section('Overview')
        print(f'  Runtime         : {runtime}')
        print(f'  Memory          : {memory}')
        print(f'  Governance      : {governance}')
        print(f'  Active clusters : {len(active_clusters)} selected')
        why = 'Detected on this machine and ready for install.' if discovery.get('status') == 'found' and runtime != 'generic' else ('Global skill surface detected.' if runtime == 'generic' and discovery.get('status') == 'found' else 'Canonical home will be created on install.')
        print(f'  Why suggested   : {why}')
        print('')
        print_section('Generated Pack')
        print(f'  Pack root       : {display_path(pack_root)}')
        print(f'  Repo config     : {display_path(output_path)}')
        print(f'  YAML summary    : {display_path(active_deployment_path)}')
        print(f'  Pack files      : {pack_summary["pack_file_count"]}')
        print('  Pack preview    :')
        for line in pack_summary['pack_tree_preview']:
            print(f'    {line}')
        print('')
        print_section('Install Destination')
        print(f'  Canonical home  : {display_path(discovery.get("canonical_runtime_home"))}')
        print(f'  Managed subtree : {display_path(discovery.get("install_target_root"))}')
        print(f'  Config target   : {display_path(discovery.get("recommended_runtime_config"))}')
        if discovery.get('recommended_skill_home'):
            print(f'  Skill target    : {display_path(discovery.get("recommended_skill_home"))}')
        print(f'  Detection       : {discovery.get("status")}')
        overwrite = 'new install' if not install_summary['target_exists'] else f"overwrite managed subtree ({install_summary['existing_file_count']} files)"
        print(f'  Overwrite impact: {overwrite}')
        print('  Existing target :')
        for line in install_summary['existing_tree_preview']:
            print(f'    {line}')
        print('')
        print_section('Cluster Activation')
        render_cluster_summary(active_clusters)
        print('')
        print('Choose next action:\n')
        labels = {
            'local_only': 'Apply locally only',
            'apply_install': 'Apply and install to runtime home',
            'back': 'Back and edit selections',
            'cancel': 'Cancel without writing files',
        }
        for idx, option in enumerate(options):
            prefix = '›' if idx == cursor else ' '
            active = ANSI_ACTIVE if idx == cursor else ''
            reset = ANSI_RESET if idx == cursor else ''
            print(f'{active}{prefix} {labels[option]}{reset}')
        render_footer(['Enter = confirm action', 'Use ↑/↓ to choose Local only, Install, Back, or Cancel', 'q = cancel installer gracefully | Ctrl+C = force stop immediately'])
        key = read_key(sys.stdin)
        if key == 'up':
            cursor = (cursor - 1) % len(options)
        elif key == 'down':
            cursor = (cursor + 1) % len(options)
        elif key == 'enter':
            print(ANSI_RESET, end='')
            return options[cursor]
        elif key in {'q', 'Q'}:
            return 'cancel'


def choose_back_step() -> str:
    options = ['runtime', 'memory', 'clusters', 'governance', 'review', 'cancel']
    cursor = 0
    while True:
        print(ANSI_CLEAR, end='')
        render_mini_header('Edit a Specific Step', 'Jump directly to the part you want to change.')
        labels = {
            'runtime': 'Edit runtime target',
            'memory': 'Edit memory mode',
            'clusters': 'Edit active clusters',
            'governance': 'Edit governance mode',
            'review': 'Return to review screen',
            'cancel': 'Cancel installer',
        }
        for idx, option in enumerate(options):
            prefix = '›' if idx == cursor else ' '
            active = ANSI_ACTIVE if idx == cursor else ''
            reset = ANSI_RESET if idx == cursor else ''
            print(f'{active}{prefix} {labels[option]}{reset}')
        render_footer(['Enter = confirm step to revisit', 'Use ↑/↓ to choose which selection to edit', 'q = return to review screen | Ctrl+C = force stop immediately'])
        key = read_key(sys.stdin)
        if key == 'up':
            cursor = (cursor - 1) % len(options)
        elif key == 'down':
            cursor = (cursor + 1) % len(options)
        elif key == 'enter':
            print(ANSI_RESET, end='')
            return options[cursor]
        elif key in {'q', 'Q'}:
            return 'review'


def render_runtime_scan_summary_compact(runtime_scan: dict[str, dict[str, Any]]) -> None:
    pass


def collect_interactive_selection(defaults: dict[str, Any], clusters: list[str], output: Path, active_deployment: Path) -> tuple[str, str, str, list[str], str]:
    runtime_scan = scan_runtime_targets(RUNTIMES)
    runtime_options = order_runtime_options(RUNTIMES, runtime_scan)
    default_runtime = defaults.get('runtime_target', 'generic')
    detected_specific = [name for name in runtime_options if name != 'generic' and runtime_scan.get(name, {}).get('status') == 'found']
    if detected_specific:
        default_runtime = detected_specific[0]
    elif runtime_scan.get(default_runtime, {}).get('status') != 'found':
        detected = [name for name in runtime_options if runtime_scan.get(name, {}).get('status') == 'found']
        if detected:
            default_runtime = detected[0]
    show_welcome_screen(output, active_deployment, runtime_scan)
    runtime = prompt_choice('Runtime target', runtime_options, default_runtime, 'runtime', runtime_scan)
    memory = prompt_choice('Memory mode', MEMORY_MODES, defaults.get('memory_mode', 'hybrid'), 'memory')
    active_clusters = prompt_clusters(clusters)
    governance = prompt_choice('Governance mode', GOVERNANCE_MODES, defaults.get('governance_mode', 'production'), 'governance')
    while True:
        discovery = discover_runtime(runtime)
        pack_root = runtime_pack_root_for(runtime, output)
        install_summary = collect_install_existing_summary(Path(discovery['install_target_root'])) if discovery.get('install_target_root') else {'target_exists': False, 'existing_file_count': 0, 'existing_tree_preview': ['(no install target)']}
        temp_config = build_config(runtime, memory, governance, active_clusters, output, active_deployment, install_mode='copy', install_applied=False, install_target_root=discovery.get('install_target_root'), pack_root=pack_root)
        output.parent.mkdir(parents=True, exist_ok=True)
        active_deployment.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(temp_config, ensure_ascii=False, indent=2) + '\n')
        write_yaml_like(active_deployment, temp_config)
        build_runtime_pack(temp_config, output, active_deployment)
        pack_summary = pack_preview_summary(pack_root)
        action = review_selections(runtime, memory, governance, active_clusters, output, active_deployment, discovery, pack_root, install_summary, pack_summary)
        if action in {'local_only', 'apply_install'}:
            return runtime, memory, governance, active_clusters, action
        if action == 'cancel':
            raise SystemExit('Interactive installer cancelled by user before write.')
        step = choose_back_step()
        if step == 'runtime':
            runtime_scan = scan_runtime_targets(RUNTIMES)
            runtime_options = order_runtime_options(RUNTIMES, runtime_scan)
            runtime = prompt_choice('Runtime target', runtime_options, runtime, 'runtime', runtime_scan)
        elif step == 'memory':
            memory = prompt_choice('Memory mode', MEMORY_MODES, memory, 'memory')
        elif step == 'clusters':
            active_clusters = prompt_clusters(clusters, default_all=False, preselected=active_clusters)
        elif step == 'governance':
            governance = prompt_choice('Governance mode', GOVERNANCE_MODES, governance, 'governance')
        elif step == 'cancel':
            raise SystemExit('Interactive installer cancelled by user before write.')


def install_central_home(pack_root: Path, target_root: Path, config: dict[str, Any]) -> dict[str, Any]:
    existing_files = sum(1 for path in target_root.rglob('*') if path.is_file()) if target_root.exists() else 0
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(pack_root, target_root, dirs_exist_ok=True, symlinks=True)
    installed_files = sum(1 for path in target_root.rglob('*') if path.is_file())
    receipt = install_receipt_payload(config, target_root, installed_files, 'central-home')
    (target_root / 'install.receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    installed_files = sum(1 for path in target_root.rglob('*') if path.is_file())
    return {'target_root': str(target_root), 'existing_file_count': existing_files, 'installed_file_count': installed_files, 'receipt_path': str(target_root / 'install.receipt.json')}


def install_runtime_pack(pack_root: Path, target_root: Path, config: dict[str, Any]) -> dict[str, Any]:
    existing_files = sum(1 for path in target_root.rglob('*') if path.is_file()) if target_root.exists() else 0
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(pack_root, target_root, dirs_exist_ok=True, symlinks=True)
    installed_files = sum(1 for path in target_root.rglob('*') if path.is_file())
    receipt = install_receipt_payload(config, target_root, installed_files, 'runtime-shim')
    (target_root / 'install.receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    installed_files = sum(1 for path in target_root.rglob('*') if path.is_file())
    return {'target_root': str(target_root), 'existing_file_count': existing_files, 'installed_file_count': installed_files, 'receipt_path': str(target_root / 'install.receipt.json')}


def main() -> int:
    parser = argparse.ArgumentParser(description='Interactive installer for Gov-Agentic AI runtime config.')
    parser.add_argument('--defaults', action='store_true', help='Use installer defaults without prompts.')
    parser.add_argument('--runtime', choices=RUNTIMES, help='Runtime target.')
    parser.add_argument('--memory', choices=MEMORY_MODES, help='Memory mode.')
    parser.add_argument('--governance', choices=GOVERNANCE_MODES, help='Governance mode.')
    parser.add_argument('--clusters', help='Comma-separated active clusters. Default: all clusters.')
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT), help='Runtime JSON output path.')
    parser.add_argument('--active-deployment', default=str(DEFAULT_ACTIVE_DEPLOYMENT), help='YAML summary output path.')
    parser.add_argument('--install-target-root', help='Override runtime shim install target root for testing or explicit deployment.')
    parser.add_argument('--central-home-root', help='Override canonical central home root.')
    parser.add_argument('--local-only', action='store_true', help='Generate local config and packs only, without installing to runtime home.')
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
        final_action = 'local_only' if args.local_only else 'apply_install'
    else:
        runtime, memory, governance, active_clusters, final_action = collect_interactive_selection(defaults, clusters, output, active_deployment)
        if args.local_only:
            final_action = 'local_only'
    unknown = sorted(set(active_clusters) - set(clusters))
    if unknown:
        raise SystemExit(f'Unknown clusters: {", ".join(unknown)}')
    discovery = discover_runtime(runtime)
    central_home_root = args.central_home_root or discovery.get('central_home_root') or str(DEFAULT_CENTRAL_HOME)
    shim_pack_root = shim_pack_root_for(runtime, output)
    central_pack_root = central_pack_root_for(output)
    install_target_root = args.install_target_root or discovery.get('install_target_root')
    initial_config = build_config(runtime, memory, governance, active_clusters, output, active_deployment, install_target_root=install_target_root, pack_root=shim_pack_root, central_home_root=central_home_root, central_pack_root=central_pack_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    active_deployment.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(initial_config, ensure_ascii=False, indent=2) + '\n')
    write_yaml_like(active_deployment, initial_config)
    central_pack_info = build_central_home_pack(initial_config)
    shim_pack_info = build_runtime_pack(initial_config, output, active_deployment)
    central_install_result = None
    shim_install_result = None
    if final_action == 'apply_install':
        central_install_result = install_central_home(Path(central_pack_info['pack_root']), Path(central_home_root), initial_config)
        if install_target_root:
            shim_install_result = install_runtime_pack(Path(shim_pack_info['pack_root']), Path(install_target_root), initial_config)
    final_config = build_config(runtime, memory, governance, active_clusters, output, active_deployment, install_mode='copy', install_applied=bool(central_install_result or shim_install_result), install_target_root=install_target_root, pack_root=Path(shim_pack_info['pack_root']), central_home_root=central_home_root, central_pack_root=Path(central_pack_info['pack_root']))
    output.write_text(json.dumps(final_config, ensure_ascii=False, indent=2) + '\n')
    write_yaml_like(active_deployment, final_config)
    Path(shim_pack_info['config_path']).write_text(json.dumps(final_config | {'runtime_pack_root': '.', 'central_pack_root': final_config['central_pack_root']}, ensure_ascii=False, indent=2) + '\n')
    Path(central_pack_info['config_path']).write_text(json.dumps(final_config | {'runtime_pack_root': final_config['runtime_pack_root'], 'central_pack_root': '.'}, ensure_ascii=False, indent=2) + '\n')
    print(f'wrote_runtime_config={relative_to_root(output)}')
    print(f'wrote_active_deployment={relative_to_root(active_deployment)}')
    print(f'runtime_target={runtime}')
    print(f'memory_mode={memory}')
    print(f'governance_mode={governance}')
    print(f'active_clusters={len(active_clusters)}')
    print(f'active_roles={len(final_config["active_roles"])}')
    print(f'active_skills={len(final_config["active_skills"])}')
    print(f'adapter_profile={final_config.get("adapter_profile_path")}')
    print(f'central_home_root={central_home_root}')
    print(f'central_pack_root={central_pack_info["pack_root"]}')
    print(f'runtime_pack_root={shim_pack_info["pack_root"]}')
    print(f'install_action={final_action}')
    if shim_install_result:
        print(f'install_target_root={shim_install_result["target_root"]}')
        print(f'install_existing_file_count={shim_install_result["existing_file_count"]}')
        print(f'install_installed_file_count={shim_install_result["installed_file_count"]}')
        print(f'install_receipt={shim_install_result["receipt_path"]}')
    if central_install_result:
        print(f'central_install_root={central_install_result["target_root"]}')
        print(f'central_install_receipt={central_install_result["receipt_path"]}')
    print(f'governance_summary={final_config.get("governance_policy", {}).get("mode_summary")}')
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\nInstaller force-stopped by user.', file=sys.stderr)
        raise SystemExit(130)
