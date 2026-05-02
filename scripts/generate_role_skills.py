#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
KB_MANIFEST = ROOT / 'knowledge-base' / 'kb_manifest.json'
ANNEX = ROOT / 'docs' / 'architecture' / 'Gov_Agentic_AI_Persona_Alias_Annex_v3.0.md'
PROMPTS = ROOT / 'prompts' / 'roles'
SKILLS = ROOT / 'skills'
ROLE_SKILLS = SKILLS / 'roles'
SHARED_SKILL = SKILLS / '_shared' / 'gov-agentic-common'

STANDARD_OUTPUT = [
    'summary',
    'evidence_map',
    'assumptions',
    'confidence_status',
    'red_flags',
    'human_touchpoint',
    'next_step',
]

ROLE_EXPECTED_ARTIFACTS = {
    'GOV-AI': ['routing decision', 'intent classification', 'action-level decision', 'handoff plan'],
    'Analis Kebijakan': ['policy brief', 'regulatory mapping', 'policy options memo'],
    'Konsultan Hukum': ['legal memo', 'clause risk review', 'authority assessment'],
    'Monitor Kepatuhan Hukum': ['compliance challenge note', 'audit evidence checklist'],
    'Perencana Program': ['KAK/ToR draft', 'program logic note', 'indicator mapping'],
    'Analis Anggaran': ['RAB review', 'SBM comparison', 'budget variance note'],
    'Monitor Kepatuhan Anggaran': ['budget compliance note', 'BPK-ready evidence checklist'],
    'Admin Pengadaan': ['procurement document checklist', 'tender preparation note'],
    'Evaluator Vendor': ['vendor evaluation memo', 'due diligence note'],
    'Penjaga Spesifikasi': ['neutral specification review', 'vendor-bias red flag note'],
    'Koordinator Data': ['data source map', 'data quality note'],
    'Analisis Statistik': ['statistical summary', 'table interpretation', 'data caveat note'],
    'GIS Analyst': ['spatial analysis note', 'map evidence summary'],
    'Penulis Naskah': ['official draft', 'formal narrative', 'revision-ready text'],
    'Notulis': ['meeting minutes', 'decision log', 'action item list'],
    'Penerjemah Kebijakan': ['plain-language policy translation', 'bilingual brief'],
    'Asisten SDM': ['HR support memo', 'personnel document checklist'],
    'Asisten Pelatihan': ['training plan', 'curriculum outline', 'participant note'],
    'Monitor Kinerja': ['KPI review', 'performance monitoring note'],
    'Liaison Publik': ['public response draft', 'stakeholder communication note'],
    'Koordinator Lapangan': ['field coordination note', 'operational status summary'],
    'Manajemen Risiko': ['risk register', 'mitigation note', 'escalation recommendation'],
    'Admin Persuratan': ['letter intake note', 'official letter draft checklist'],
    'Asisten Disposisi': ['disposition routing note', 'SLA handoff plan'],
    'Arsiparis Digital': ['archive metadata note', 'records retention checklist'],
    'Agenda & Protokol': ['agenda plan', 'protocol checklist'],
    'Admin Layanan Internal': ['internal service ticket summary', 'fulfillment checklist'],
    'Monitor SLA Tata Usaha': ['SLA status note', 'aging task report'],
    'Bot Eskalasi': ['conflict resolution note', 'escalation path', 'human takeover memo'],
}

ROLE_RED_FLAGS = {
    'GOV-AI': ['unclear intent', 'missing data classification', 'action level L3/L4 without approval path'],
    'Bot Eskalasi': ['unresolved role conflict', 'blocked compliance/legal path', 'missing human owner'],
}

DEFAULT_RED_FLAGS = [
    'missing or outdated source evidence',
    'request requires L3/L4 human approval',
    'restricted or sensitive data appears without handling decision',
    'output could create legal, fiscal, procurement, reputational, or public impact',
]


def slugify(value: str) -> str:
    value = value.lower().replace('&', 'dan')
    value = re.sub(r'[^a-z0-9]+', '-', value).strip('-')
    return re.sub(r'-+', '-', value)


def skill_dir_name(role: dict[str, str]) -> str:
    role_slug = role['path'].split('/')[-1]
    return f"{role['cluster']}__{role_slug}"


def skill_name(role: dict[str, str]) -> str:
    return f"gov-{slugify(role['role'])}-{slugify(role['alias'])}"


def prompt_path_for(role: dict[str, str]) -> Path | None:
    prefix = f"{role['cluster']}__"
    alias_suffix = f"_{slugify(role['alias'])}.md"
    candidates = sorted(PROMPTS.glob(f"{prefix}*{alias_suffix}"))
    return candidates[0] if candidates else None


def parse_annex_profiles() -> dict[str, dict[str, Any]]:
    text = ANNEX.read_text()
    sections = re.split(r'\n(?=## )', text)
    profiles: dict[str, dict[str, Any]] = {}
    for section in sections:
        if not section.startswith('## '):
            continue
        lines = section.splitlines()
        title = lines[0].replace('## ', '').strip()
        if ' - ' not in title:
            continue
        role, alias = title.split(' - ', 1)
        data: dict[str, Any] = {'role': role.strip(), 'alias': alias.strip(), 'raw_title': title}
        for line in lines[1:]:
            m = re.match(r'- ([^:]+):\s*(.*)', line)
            if m:
                key = slugify(m.group(1)).replace('-', '_')
                data[key] = m.group(2).strip()
        profiles[f"{role.strip()}::{alias.strip()}"] = data
    return profiles


def write_if_allowed(path: Path, content: str, force: bool, created: list[str], skipped: list[str]) -> None:
    if path.exists() and not force:
        skipped.append(str(path.relative_to(ROOT)))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    created.append(str(path.relative_to(ROOT)))


def yaml_quote(value: str) -> str:
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'


def role_kind(role: str) -> str:
    if role == 'GOV-AI':
        return 'orchestrator'
    if role == 'Bot Eskalasi':
        return 'escalation'
    lowered = role.lower()
    if 'monitor' in lowered or 'kepatuhan' in lowered:
        return 'compliance-monitor'
    return 'specialist'


def description_for(role: dict[str, str], profile: dict[str, Any]) -> str:
    trigger = profile.get('trigger_summary', '')
    focus = profile.get('fokus', '')
    return (
        f"Use this Gov-Agentic AI role skill for {role['role']} ({role['alias']}) in the "
        f"{role['cluster']} cluster. Use when tasks involve {focus or 'role-specific government work'}, "
        f"trigger keywords such as {trigger or role['role']}, and outputs requiring evidence maps, "
        "confidence status, red flags, audit logging, and human-in-the-loop decisions."
    )


def skill_md(role: dict[str, str], profile: dict[str, Any], prompt_rel: str, knowledge_rel: str) -> str:
    kind = role_kind(role['role'])
    if kind == 'orchestrator':
        workflow = [
            'Classify intent, data class, action level, urgency, and risk.',
            'Route to the correct specialist or monitor role; create or preserve `trace_id`.',
            'Detect conflicts, missing evidence, sensitive data, and L3/L4 actions.',
            'Require human approval before formal or externally impactful action.',
        ]
    elif kind == 'escalation':
        workflow = [
            'Read the conflict, blocker, or escalation context.',
            'Identify winning rule: compliance, legal, fiscal, security, or human authority.',
            'Produce a final escalation path and human takeover point.',
            'Never resolve beyond authority; mark unresolved conflicts as hold/escalate.',
        ]
    elif kind == 'compliance-monitor':
        workflow = [
            'Challenge the draft, source evidence, assumptions, and compliance posture.',
            'Check source validity, freshness, auditability, and policy fit.',
            'Mark red flags and recommend proceed, revise, hold, block, or escalate.',
            'Prefer conservative handling when evidence is weak or impact is high.',
        ]
    else:
        workflow = [
            'Understand the task and confirm role fit from the request and triggers.',
            'Load only the necessary role prompt, role profile, and knowledge map.',
            'Ground the output in role knowledge and shared references before drafting.',
            'Return the standard output contract with evidence, confidence, and HITL status.',
        ]
    workflow_md = '\n'.join(f'{i+1}. {item}' for i, item in enumerate(workflow))
    output_md = '\n'.join(f'- `{item}`' for item in STANDARD_OUTPUT)
    return f'''---
name: {skill_name(role)}
description: {yaml_quote(description_for(role, profile))}
---

# {role['role']} ({role['alias']})

## Purpose
Act as the Gov-Agentic AI role skill for **{role['role']} ({role['alias']})** in the `{role['cluster']}` cluster. Use this skill to perform role-specific government analysis, drafting, review, routing, or escalation while preserving source traceability and human authority.

## When to Use
Use this skill when the user request matches this role, its alias, cluster, focus area, or trigger keywords in `references/role-profile.md`.

## Required Inputs
- Task summary or user request
- Available evidence or source documents
- Data classification if known
- Action level if known
- Human reviewer or approving role if known

## Workflow
{workflow_md}

## Required Output
Every substantive output must include:
{output_md}

## Guardrails
- Apply action-level, data-classification, HITL, and audit guidance from `../../../_shared/gov-agentic-common/SKILL.md` when available.
- Do not treat AI output as a formal decision; humans retain final authority.
- Do not fabricate legal basis, budget numbers, vendor facts, or source citations.
- Mark confidence `Low` when evidence is missing, outdated, conflicting, or outside the role boundary.
- Stop or escalate when restricted/sensitive data, L3/L4 action, unresolved conflict, or public/legal/fiscal impact appears.

## References
Load only what is needed:
- `references/role-profile.md` for persona, focus, triggers, expected artifacts, and role red flags.
- `references/knowledge-map.md` for role knowledge and shared-knowledge paths.
- `references/output-contract.md` for the required response structure.
- `{prompt_rel}` for the existing prompt template if the runtime can read repository files.
- `{knowledge_rel}` for curated role knowledge.
'''


def role_profile_md(role: dict[str, str], profile: dict[str, Any]) -> str:
    artifacts = ROLE_EXPECTED_ARTIFACTS.get(role['role'], ['role-specific review note', 'evidence-grounded draft'])
    red_flags = ROLE_RED_FLAGS.get(role['role'], DEFAULT_RED_FLAGS)
    trigger = profile.get('trigger_summary', '')
    fields = [
        ('Role', role['role']),
        ('Alias', role['alias']),
        ('Cluster', role['cluster']),
        ('Focus', profile.get('fokus', '')), 
        ('Karakter Kerja', profile.get('karakter_kerja', '')), 
        ('Thinking Level', profile.get('thinking_level', '')), 
        ('Creative Level', profile.get('creative_level', '')), 
        ('Voice and Tone', profile.get('voice_and_tone', '')), 
        ('Critical Level', profile.get('critical_level', '')), 
        ('Analytical Thinking', profile.get('analytical_thinking', '')), 
        ('Strategic Level', profile.get('strategic_level', '')), 
        ('Trigger Keywords', trigger),
    ]
    lines = [f"# Role Profile: {role['role']} ({role['alias']})", '']
    for key, value in fields:
        lines.append(f'- **{key}:** {value or "TBD"}')
    lines.extend(['', '## Expected Artifacts'])
    lines.extend(f'- {item}' for item in artifacts)
    lines.extend(['', '## Role-Specific Red Flags'])
    lines.extend(f'- {item}' for item in red_flags)
    lines.append('')
    return '\n'.join(lines)


def output_contract_md(role: dict[str, str]) -> str:
    return f'''# Output Contract

Use this structure for {role['role']} ({role['alias']}) outputs.

## Required Fields
- `summary`: concise answer or artifact summary.
- `evidence_map`: sources, dates, relevance, and gaps.
- `assumptions`: assumptions made and what would change them.
- `confidence_status`: High, Medium, or Low.
- `red_flags`: compliance, legal, fiscal, data, public, or operational risks.
- `human_touchpoint`: who must review, approve, reject, hold, or take over.
- `next_step`: proceed, revise, hold, escalate, block, or ask for source.

## Minimum Rule
If a required field cannot be completed, explicitly write `Not available` and explain the gap under `red_flags` or `assumptions`.
'''


def knowledge_map_md(role: dict[str, str], prompt_rel: str, knowledge_rel: str) -> str:
    return f'''# Knowledge Map

## Role Prompt
- `{prompt_rel}`

## Role Knowledge Folder
- `{knowledge_rel}`

## Shared Knowledge Links
- `{knowledge_rel}/_shared-links`

## Suggested Reads by Need
- Regulations/policies: `{knowledge_rel}/02-regulations-and-policies` and `_shared-links/01-regulasi-umum`
- Templates/examples: `{knowledge_rel}/03-templates-and-examples` and `_shared-links/03-template-global`
- SOP/workflows: `{knowledge_rel}/04-sop-and-workflows` and `_shared-links/02-sop-umum`
- Reference data: `{knowledge_rel}/05-reference-data` and `_shared-links/04-data-dictionaries`
- Output samples: `{knowledge_rel}/06-output-samples` and `_shared-links/08-golden-outputs`
- Review notes: `{knowledge_rel}/07-review-notes`
- Ingestion-ready sources: `{knowledge_rel}/08-ingestion-ready`

## Retrieval Rule
Prefer role-specific evidence first. Use shared evidence when it is canonical, cross-role, or the role folder is incomplete.
'''


def shared_skill_md() -> str:
    return '''---
name: gov-agentic-common
description: "Use this shared Gov-Agentic AI skill for action-level policy, data classification, HITL gates, audit logging, confidence handling, and common guardrails across all government role skills."
---

# Gov-Agentic Common Guardrails

## Purpose
Provide shared policy for all Gov-Agentic AI role skills. This skill is not a replacement for a role skill; it supplies common decision gates and output integrity rules.

## Use When
Use when a request involves government documents, public-sector decisions, sensitive/internal data, formal drafting, legal/fiscal/procurement impact, audit requirements, or cross-role escalation.

## Core Rules
- Humans retain formal authority.
- L3/L4 actions require Human-in-the-Loop approval.
- Sensitive data requires restricted handling and access audit.
- Claims need evidence maps.
- Low evidence means low confidence, not confident guessing.
- Conflicts escalate through the conflict matrix or Bot Eskalasi/Winda.

## References
- `references/action-level-policy.md`
- `references/data-classification.md`
- `references/hitl-and-audit.md`
'''


def generate(force: bool, check: bool) -> dict[str, Any]:
    manifest = json.loads(KB_MANIFEST.read_text())
    profiles = parse_annex_profiles()
    created: list[str] = []
    skipped: list[str] = []
    skills: list[dict[str, Any]] = []

    planned = []
    for role in manifest['roles']:
        key = f"{role['role']}::{role['alias']}"
        profile = profiles.get(key, {})
        prompt = prompt_path_for(role)
        if not prompt:
            raise SystemExit(f"Missing prompt for {role}")
        skill_dir = ROLE_SKILLS / skill_dir_name(role)
        prompt_rel = str(prompt.relative_to(ROOT))
        knowledge_rel = str((ROOT / 'knowledge-base' / role['path']).relative_to(ROOT))
        planned.append(str(skill_dir.relative_to(ROOT)))
        skills.append({
            'name': skill_name(role),
            'role': role['role'],
            'alias': role['alias'],
            'cluster': role['cluster'],
            'skill_path': str(skill_dir.relative_to(ROOT)),
            'skill_md': str((skill_dir / 'SKILL.md').relative_to(ROOT)),
            'prompt_path': prompt_rel,
            'knowledge_path': knowledge_rel,
        })
        if check:
            continue
        for directory in [skill_dir / 'references', skill_dir / 'assets', skill_dir / 'scripts']:
            directory.mkdir(parents=True, exist_ok=True)
        for keep in [skill_dir / 'assets' / '.gitkeep', skill_dir / 'scripts' / '.gitkeep']:
            if not keep.exists():
                keep.write_text('')
                created.append(str(keep.relative_to(ROOT)))
        write_if_allowed(skill_dir / 'SKILL.md', skill_md(role, profile, prompt_rel, knowledge_rel), force, created, skipped)
        write_if_allowed(skill_dir / 'references' / 'role-profile.md', role_profile_md(role, profile), force, created, skipped)
        write_if_allowed(skill_dir / 'references' / 'output-contract.md', output_contract_md(role), force, created, skipped)
        write_if_allowed(skill_dir / 'references' / 'knowledge-map.md', knowledge_map_md(role, prompt_rel, knowledge_rel), force, created, skipped)

    skill_manifest = {
        'version': 'v1.0',
        'runtime_target': ['Claude', 'Codex', 'OpenClaw', 'Hermes Agent', 'Antigravity'],
        'skill_count': len(skills),
        'shared_skill': 'skills/_shared/gov-agentic-common/SKILL.md',
        'skills': skills,
    }
    if not check:
        for directory in [SHARED_SKILL / 'references']:
            directory.mkdir(parents=True, exist_ok=True)
        write_if_allowed(SHARED_SKILL / 'SKILL.md', shared_skill_md(), force, created, skipped)
        write_if_allowed(SHARED_SKILL / 'references' / 'action-level-policy.md', '''# Action-Level Policy

- L0: read, classify, route, summarize. Automatic with minimal log.
- L1: low-risk draft. Automatic but marked as draft.
- L2: recommendation. Requires human review before operational use.
- L3: formal artifact preparation. Requires human approval before finalization.
- L4: external or impactful execution. Requires explicit approval, full audit, and rollback/hold path.

Block if the request violates law/SOP, lacks critical evidence, includes unauthorized sensitive data, or attempts to bypass audit/approval.
''', force, created, skipped)
        write_if_allowed(SHARED_SKILL / 'references' / 'data-classification.md', '''# Data Classification

- Public: usable for drafting/search with normal logging.
- Internal: authenticated use with RBAC and audit log.
- Restricted: private zone or sovereign cloud; masking required for broader use.
- Sensitive: default no external model processing; requires explicit approval, minimization, redaction, and access audit.
''', force, created, skipped)
        write_if_allowed(SHARED_SKILL / 'references' / 'hitl-and-audit.md', '''# HITL and Audit

Human-in-the-Loop is mandatory for L3/L4, sensitive data, public/legal/fiscal/procurement impact, unresolved conflicts, and low-confidence evidence.

Audit records should include trace_id, requester, role chain, evidence map, red flags, conflict path, human reviewer, decision, artifact version, and final status.
''', force, created, skipped)
        write_if_allowed(SKILLS / 'skill_manifest.json', json.dumps(skill_manifest, ensure_ascii=False, indent=2) + '\n', force, created, skipped)
        write_if_allowed(SKILLS / 'README.md', skills_readme(), force, created, skipped)

    return {'planned': planned, 'created': created, 'skipped': skipped, 'skill_count': len(skills)}


def skills_readme() -> str:
    return '''# Gov-Agentic AI Skills

This folder contains universal `SKILL.md` skills for Gov-Agentic AI role replication across Claude, Codex, OpenClaw, Hermes Agent, and Antigravity-style agent runtimes.

## Structure
- `roles/` contains 29 role skills.
- `_shared/gov-agentic-common` contains shared guardrails.
- `skill_manifest.json` is the machine-readable registry.

## Usage
Install or import the role skill folder required by the target runtime. Each role skill points back to this repo's prompts and knowledge-base paths instead of duplicating large knowledge documents.

## Validation
Run:

```bash
python3 scripts/verify_skills.py
```
'''


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate universal Gov-Agentic AI role skills.')
    parser.add_argument('--force', action='store_true', help='Overwrite existing generated files.')
    parser.add_argument('--check', action='store_true', help='Dry-run and print planned skill folders only.')
    args = parser.parse_args()
    result = generate(force=args.force, check=args.check)
    print(f"skill_count={result['skill_count']}")
    if args.check:
        for item in result['planned']:
            print(item)
        return
    print(f"created_or_updated={len(result['created'])}")
    print(f"skipped_existing={len(result['skipped'])}")

if __name__ == '__main__':
    main()
