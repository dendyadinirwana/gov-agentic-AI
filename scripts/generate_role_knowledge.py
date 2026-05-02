#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
KB_ROOT = ROOT / 'knowledge-base'
SKILLS_ROOT = ROOT / 'skills' / 'roles'
KB_MANIFEST = KB_ROOT / 'kb_manifest.json'
SKILL_MANIFEST = ROOT / 'skills' / 'skill_manifest.json'
QUALITY_MANIFEST = KB_ROOT / 'knowledge_quality_manifest.json'

STARTER_FILES = {
    '00-readme/role-charter.md': 'role_charter',
    '01-source-documents/source-map.md': 'source_map',
    '02-regulations-and-policies/policy-map.md': 'policy_map',
    '03-templates-and-examples/artifact-catalog.md': 'artifact_catalog',
    '04-sop-and-workflows/workflow-map.md': 'workflow_map',
    '04-sop-and-workflows/decision-boundaries.md': 'decision_boundaries',
    '05-reference-data/reference-catalog.md': 'reference_catalog',
    '06-output-samples/starter-output-examples.md': 'starter_outputs',
    '07-review-notes/quality-checklist.md': 'quality_checklist',
    '08-ingestion-ready/intake-guide.md': 'intake_guide',
    '09-archive/archive-rules.md': 'archive_rules',
}

SHARED_FILES = {
    '00-governance-and-routing/role-routing-matrix.md': 'shared_routing',
    '01-regulasi-umum/source-hierarchy.md': 'shared_regulations',
    '02-sop-umum/sop-primitives.md': 'shared_sops',
    '03-template-global/global-artifact-patterns.md': 'shared_templates',
    '04-data-dictionaries/common-data-dictionary.md': 'shared_dictionary',
    '05-risk-and-compliance/risk-trigger-matrix.md': 'shared_risks',
    '06-audit-and-observability/audit-observability-contract.md': 'shared_audit',
    '08-golden-outputs/golden-output-patterns.md': 'shared_outputs',
}

READINESS_ORDER = ['seed', 'usable', 'operational', 'high-confidence']
ROLE_CLASS_RULES = {
    'router': {'summary': 'router/orchestrator', 'autonomy': 'route, classify, and structure work; never self-approve consequential action'},
    'specialist': {'summary': 'specialist/executor', 'autonomy': 'analyze and draft within domain; never finalize externally impactful action without review'},
    'monitor': {'summary': 'monitor/compliance', 'autonomy': 'challenge, verify, and recommend block/hold; never silently waive control failures'},
    'escalation': {'summary': 'escalation/fallback', 'autonomy': 'stabilize conflict paths and define human takeover; never invent an approver or bypass escalation'},
}

CLUSTER_SOURCE_HINTS = {
    'top-layer': ['system prompt', 'routing logs', 'task intake context', 'cluster manifests'],
    'kebijakan-dan-hukum': ['regulation extracts', 'contract drafts', 'legal memos', 'policy change notes'],
    'perencanaan-dan-anggaran': ['RKA/RAB sheets', 'SBM references', 'budget realization notes', 'program targets'],
    'pengadaan-barang-dan-jasa': ['procurement packages', 'vendor evidence', 'technical specifications', 'evaluation notes'],
    'data-dan-analitik': ['datasets', 'metadata sheets', 'statistical methods', 'geospatial layers'],
    'komunikasi-dan-dokumen': ['minutes', 'draft narratives', 'translation briefs', 'communication approvals'],
    'sdm-dan-kinerja': ['personnel records', 'training plans', 'performance indicators', 'workload summaries'],
    'hubungan-eksternal-dan-lapangan': ['public complaints', 'field reports', 'stakeholder maps', 'incident notes'],
    'tata-usaha': ['incoming letters', 'disposition memos', 'service tickets', 'archive indexes'],
    'bottom-gate': ['escalation notes', 'approval chains', 'control breach reports', 'blocker logs'],
}

ARTIFACT_HINTS = {
    'GOV-AI': ['routing decision', 'intent classification', 'action-level decision', 'handoff brief'],
    'Analis Kebijakan': ['policy brief', 'issue tree', 'option comparison', 'policy alignment note'],
    'Konsultan Hukum': ['legal memo', 'clause risk review', 'authority assessment', 'human review note'],
    'Monitor Kepatuhan Hukum': ['compliance finding log', 'hold recommendation', 'source-validity challenge', 'remediation note'],
    'Perencana Program': ['KAK/ToR outline', 'logic model note', 'program alignment map', 'approval checklist'],
    'Analis Anggaran': ['RAB review', 'SBM comparison', 'variance note', 'cost assumption table'],
    'Monitor Kepatuhan Anggaran': ['budget compliance check', 'pagu-risk alert', 'blocking note', 'exception summary'],
    'Admin Pengadaan': ['procurement intake note', 'document completeness checklist', 'package status recap', 'approval bundle'],
    'Evaluator Vendor': ['vendor evidence review', 'vendor comparison matrix', 'conflict-of-interest alert', 'recommendation note'],
    'Penjaga Spesifikasi': ['specification review', 'scope drift note', 'brand-neutrality check', 'technical clarification list'],
    'Koordinator Data': ['dataset readiness note', 'data request routing', 'metadata completeness report', 'integration handoff'],
    'Analisis Statistik': ['statistical analysis note', 'assumption statement', 'result interpretation brief', 'quality flag log'],
    'GIS Analyst': ['map interpretation brief', 'layer validation note', 'spatial risk summary', 'field evidence request'],
    'Penulis Naskah': ['draft narrative', 'speech note', 'briefing text', 'revision-ready manuscript'],
    'Notulis': ['meeting minutes', 'decision log', 'action tracker', 'attendance recap'],
    'Penerjemah Kebijakan': ['bilingual policy note', 'term equivalence table', 'translation risk note', 'review-ready translation'],
    'Asisten SDM': ['HR admin summary', 'staffing checklist', 'eligibility note', 'handoff memo'],
    'Asisten Pelatihan': ['training plan draft', 'participant checklist', 'learning objective note', 'follow-up recap'],
    'Monitor Kinerja': ['performance variance alert', 'indicator health note', 'follow-up recommendation', 'review summary'],
    'Liaison Publik': ['stakeholder response draft', 'public inquiry summary', 'sensitivity note', 'handoff note'],
    'Koordinator Lapangan': ['field coordination brief', 'deployment checklist', 'incident escalation note', 'status recap'],
    'Manajemen Risiko': ['risk register update', 'mitigation recommendation', 'escalation trigger note', 'control gap summary'],
    'Admin Persuratan': ['letter intake note', 'official letter draft checklist', 'numbering request', 'dispatch summary'],
    'Asisten Disposisi': ['disposition summary', 'routing recommendation', 'follow-up tracker', 'recipient checklist'],
    'Arsiparis Digital': ['archive index update', 'retention tag note', 'retrieval record', 'final filing summary'],
    'Agenda & Protokol': ['agenda plan', 'protocol checklist', 'VIP coordination note', 'event flow summary'],
    'Admin Layanan Internal': ['service request recap', 'fulfillment note', 'SLA status summary', 'handoff checklist'],
    'Monitor SLA Tata Usaha': ['SLA breach alert', 'service aging note', 'hold/escalation recommendation', 'review summary'],
    'Bot Eskalasi': ['conflict resolution note', 'escalation path', 'human takeover memo', 'block/hold recommendation'],
}

ROLE_SPECIFICS = {
    'Yayak': {'mandate': 'Classify incoming work, set action level, identify the best downstream role set, and preserve traceability.', 'non_scope': ['acting as final approver', 'inventing policy authority', 'publishing externally without human review'], 'handoff': ['specialist role owner', 'monitor/compliance role', 'Winda for unresolved conflict'], 'trusted_shared': ['00-governance-and-routing', '05-risk-and-compliance', '06-audit-and-observability', '08-golden-outputs']},
    'Winda': {'mandate': 'Resolve routing deadlocks, approval ambiguity, and blocked compliance paths; define the human takeover lane.', 'non_scope': ['overriding legal or fiscal controls', 'closing a case without naming a human owner', 'executing the specialist task itself'], 'handoff': ['human approver', 'cluster lead role', 'relevant monitor role'], 'trusted_shared': ['00-governance-and-routing', '05-risk-and-compliance', '06-audit-and-observability']},
    'Audy': {'mandate': 'Assess legal risk, clause safety, legal authority, and when formal legal review is mandatory.', 'non_scope': ['issuing binding legal opinion as final authority', 'authorizing signature', 'accepting unsupported contract facts'], 'handoff': ['human legal reviewer', 'Edi for compliance challenge', 'Winda if approval path is unclear'], 'trusted_shared': ['01-regulasi-umum', '05-risk-and-compliance', '06-audit-and-observability']},
    'Anastasia': {'mandate': 'Review RAB, cost assumptions, pagu fit, tax treatment, and budget clarity before approval.', 'non_scope': ['approving final budget commitment', 'inventing market price evidence', 'waiving budget controls'], 'handoff': ['Nanang for compliance check', 'Faris for program alignment', 'human KPA/PPK reviewer'], 'trusted_shared': ['01-regulasi-umum', '03-template-global', '05-risk-and-compliance']},
    'Harrisal': {'mandate': 'Control intake, numbering, and administrative completeness for official correspondence.', 'non_scope': ['signing on behalf of officials', 'sending official letters without approver confirmation', 'changing letter intent without source instruction'], 'handoff': ['Alfian for drafting quality', 'Woro for disposition path', 'Sovia for final archive'], 'trusted_shared': ['02-sop-umum', '03-template-global', '06-audit-and-observability']},
}

@dataclass
class RoleContext:
    path: str
    cluster: str
    role: str
    alias: str
    skill_slug: str
    skill_dir: Path
    kb_dir: Path
    role_class: str
    focus: str
    triggers: list[str]
    expected_artifacts: list[str]
    red_flags: list[str]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def clean_inline(value: str) -> str:
    return value.replace('**', '').strip()


def parse_role_profile(skill_dir: Path) -> dict[str, Any]:
    profile = skill_dir / 'references' / 'role-profile.md'
    text = profile.read_text()
    info: dict[str, Any] = {'triggers': [], 'artifacts': [], 'red_flags': [], 'focus': ''}
    for line in text.splitlines():
        if line.startswith('- **Focus:**'):
            info['focus'] = clean_inline(line.split(':', 1)[1])
        elif line.startswith('- **Trigger Keywords:**'):
            info['triggers'] = [clean_inline(item) for item in line.split(':', 1)[1].split(',') if item.strip()]
    current = None
    for line in text.splitlines():
        if line.startswith('## Expected Artifacts'):
            current = 'artifacts'
            continue
        if line.startswith('## Role-Specific Red Flags'):
            current = 'red_flags'
            continue
        if line.startswith('## '):
            current = None
        if current in {'artifacts', 'red_flags'} and line.startswith('- '):
            info[current].append(line[2:].strip())
    return info


def role_class(cluster: str, role: str, alias: str) -> str:
    role_lower = role.lower()
    alias_lower = alias.lower()
    if cluster == 'top-layer' or alias_lower == 'yayak':
        return 'router'
    if cluster == 'bottom-gate' or alias_lower == 'winda' or 'eskalasi' in role_lower:
        return 'escalation'
    if role_lower.startswith('monitor') or 'risiko' in role_lower:
        return 'monitor'
    return 'specialist'


def build_contexts() -> list[RoleContext]:
    kb_manifest = load_json(KB_MANIFEST)
    skills_manifest = load_json(SKILL_MANIFEST)
    skill_lookup = {item['knowledge_path']: item for item in skills_manifest['skills']}
    contexts = []
    for role in kb_manifest['roles']:
        kb_path = f"knowledge-base/{role['path']}"
        skill = skill_lookup[kb_path]
        skill_dir = ROOT / skill['skill_path']
        profile = parse_role_profile(skill_dir)
        contexts.append(RoleContext(
            path=role['path'],
            cluster=role['cluster'],
            role=role['role'],
            alias=role['alias'],
            skill_slug=Path(skill['skill_path']).name,
            skill_dir=skill_dir,
            kb_dir=ROOT / kb_path,
            role_class=role_class(role['cluster'], role['role'], role['alias']),
            focus=profile['focus'] or role['role'],
            triggers=profile['triggers'],
            expected_artifacts=profile['artifacts'] or ARTIFACT_HINTS.get(role['role'], [f'{role['role']} working note']),
            red_flags=profile['red_flags'] or ['missing evidence', 'unclear authority', 'sensitive impact without approval path'],
        ))
    return contexts


def readme_relative(target: Path, other: Path) -> str:
    return str(other.relative_to(ROOT))




def available_shared_links(role: RoleContext) -> list[str]:
    shared_dir = role.kb_dir / '_shared-links'
    if not shared_dir.exists():
        return []
    return sorted(item.name for item in shared_dir.iterdir())

def special(role: RoleContext) -> dict[str, Any]:
    base = ROLE_SPECIFICS.get(role.alias, {})
    default_non_scope = [
        'making final external decisions without human approval',
        'overriding data classification or retention controls',
        'creating facts, citations, or approvals that do not exist',
    ]
    default_handoff = ['relevant cluster owner', 'monitor/compliance role', 'Winda when escalation is unresolved']
    default_shared = ['00-governance-and-routing', '01-regulasi-umum', '02-sop-umum', '08-golden-outputs']
    shared_links = set(available_shared_links(role))
    preferred = base.get('trusted_shared', default_shared)
    trusted_shared = [item for item in preferred if item in shared_links] or sorted(shared_links)[:4]
    return {
        'mandate': base.get('mandate', f"Operate as {ROLE_CLASS_RULES[role.role_class]['summary']} for {role.role} in the {role.cluster} cluster, grounded in evidence and role boundaries."),
        'non_scope': base.get('non_scope', default_non_scope),
        'handoff': base.get('handoff', default_handoff),
        'trusted_shared': trusted_shared,
    }


def render_role_charter(role: RoleContext) -> str:
    s = special(role)
    source_hints = CLUSTER_SOURCE_HINTS.get(role.cluster, ['official source documents', 'role workflow notes'])
    return f"""# Role Charter — {role.role} ({role.alias})

## Mandate
{ s['mandate'] }

## Operational Role Class
- Class: {ROLE_CLASS_RULES[role.role_class]['summary']}
- Cluster: `{role.cluster}`
- Focus: {role.focus}
- First trusted inputs: {', '.join(source_hints[:3])}

## Scope
- Receive and structure work related to {role.focus.lower()}.
- Produce grounded outputs listed in `../03-templates-and-examples/artifact-catalog.md`.
- Route or escalate when confidence, authority, or source quality is insufficient.

## Non-Scope
""" + '\n'.join(f"- {item}" for item in s['non_scope']) + f"""

## Handoff Boundaries
Primary handoff targets:
""" + '\n'.join(f"- {item}" for item in s['handoff']) + f"""

Shared references to consult first:
""" + '\n'.join(f"- `../_shared-links/{item}`" for item in s['trusted_shared']) + f"""

## Minimum Inputs Before Acting
- Clear task or case objective
- Evidence or source references
- Data classification if available
- Approval owner when action is consequential
- Time/SLA context if the work is operational

## Role Readiness Intent
This starter charter is repo-authored so the role is usable on first install. Replace or enrich it with local policy, institutional naming, and official source provenance as adoption matures.
"""


def render_source_map(role: RoleContext) -> str:
    s = special(role)
    local_overrides = [
        '`../02-regulations-and-policies/policy-map.md` for role-specific policy interpretation',
        '`../04-sop-and-workflows/workflow-map.md` for actual operating sequence',
        '`../06-output-samples/starter-output-examples.md` for response shaping',
    ]
    return f"""# Source Map — {role.role} ({role.alias})

## Source Priority Rules
1. Role-local primary evidence in `../01-source-documents`.
2. Role-local policy interpretation in `../02-regulations-and-policies`.
3. Shared canonical references linked from `_shared-links`.
4. Templates and golden outputs for formatting support only.
5. If evidence conflicts, stop and escalate instead of reconciling silently.

## Canonical vs Supporting Sources
- Canonical: signed/issued regulations, official workflow instructions, approved templates, final approved records.
- Supporting: draft notes, prior examples, working spreadsheets, meeting notes, inferred summaries.
- Non-authoritative: unsourced claims, screenshots without provenance, copied text with no issuing owner.

## Mandatory Shared Directories
""" + ('\n'.join(f"- `../_shared-links/{item}`" for item in s['trusted_shared']) if s['trusted_shared'] else '- none linked yet') + f"""

## Optional Shared Directories
""" + '\n'.join(f"- `../_shared-links/{item}`" for item in available_shared_links(role) if item not in s['trusted_shared']) + f"""

## Local Overrides
""" + '\n'.join(f"- {item}" for item in local_overrides) + f"""

## Intake Inventory Expectations
- Track source title, owner, issue date, revision status, and classification.
- Prefer filenames that preserve provenance and are stable for retrieval.
- Move stale or replaced records to `../09-archive` with a note explaining why.
"""


def render_policy_map(role: RoleContext) -> str:
    policy_focus = {
        'router': 'routing authority, action-level boundaries, and cross-role governance',
        'specialist': f'{role.focus.lower()} decisions, required approvals, and domain control points',
        'monitor': 'control failures, exception handling, and hold/block conditions',
        'escalation': 'escalation authority, approval chains, and takeover criteria',
    }[role.role_class]
    return f"""# Policy Map — {role.role} ({role.alias})

## Role-Relevant Policy Themes
- Primary policy concern: {policy_focus}
- Secondary concern: data classification, retention, and auditability
- Shared baseline: `../_shared-links/01-regulasi-umum`

## Decision-Impacting Policy Checklist
- Is there a current, official source for the requested action?
- Is the data class known and acceptable for this processing path?
- Does this output create legal, fiscal, procurement, public, or reputational impact?
- Does a named human approver exist for L3/L4 decisions?
- Is the requested action inside this role's mandate and non-scope boundaries?

## Role-Specific Policy Watchouts
""" + '\n'.join(f"- {flag}" for flag in role.red_flags[:4]) + f"""

## When to Escalate Immediately
- Policy basis is missing, outdated, or conflicting.
- Evidence quality is too weak to support a consequential output.
- The request implies approval, publication, signature, payment, procurement award, disciplinary action, or legal commitment.
- A human owner cannot be identified.
"""


def render_artifact_catalog(role: RoleContext) -> str:
    examples = role.expected_artifacts or ARTIFACT_HINTS.get(role.role, [])
    return f"""# Artifact Catalog — {role.role} ({role.alias})

## Primary Artifacts
""" + '\n'.join(f"- {item}" for item in examples) + f"""

## Template Expectations
- Start from role-local templates when available.
- Fall back to `../_shared-links/03-template-global` for formatting patterns.
- Keep the mandatory output contract: summary, evidence map, assumptions, confidence, red flags, human touchpoint, next step.

## Minimum Artifact Metadata
- source reference(s)
- version or revision date
- drafter role and reviewer role
- action level / impact level
- status: draft, review, hold, approved, archived

## Consumption Notes
- Treat examples as structure aids, not legal or administrative authority.
- If the task is novel, create a working template in this folder and record the provenance in `../08-ingestion-ready/intake-guide.md`.
"""


def render_workflow_map(role: RoleContext) -> str:
    flow = {
        'router': ['Receive request and classify intent', 'Set data class and action level', 'Route to best-fit role set', 'Preserve trace_id and expected human touchpoint'],
        'specialist': ['Confirm scope and source quality', 'Analyze or draft using role-local knowledge', 'Mark assumptions, confidence, and red flags', 'Hand off to reviewer/approver and archive the rationale'],
        'monitor': ['Read the working artifact and source basis', 'Challenge control gaps and unsupported claims', 'Recommend pass/hold/block with evidence', 'Escalate unresolved issues to Winda or human owner'],
        'escalation': ['Read blocker, conflict, or hold context', 'Identify missing authority or unresolved contradiction', 'Name the correct human takeover owner', 'Produce escalation path and stop autonomous execution'],
    }[role.role_class]
    approval = {
        'router': 'Human approval is required before any routed work becomes an external or binding action.',
        'specialist': 'Human review is required for any externally impactful or binding output.',
        'monitor': 'Hold/block recommendations should be acknowledged by a human owner before release decisions.',
        'escalation': 'Escalation is complete only after a human owner is explicitly named.',
    }[role.role_class]
    return f"""# Workflow Map — {role.role} ({role.alias})

## Standard Operating Flow
""" + '\n'.join(f"{idx}. {step}" for idx, step in enumerate(flow, start=1)) + f"""

## Approval Path
- Default: role drafts or reviews -> relevant human owner reviews -> final authority approves.
- {approval}
- If the human owner is unknown, route to `../_shared-links/00-governance-and-routing` and escalate.

## Escalation Triggers
""" + '\n'.join(f"- {flag}" for flag in role.red_flags[:5]) + f"""

## Completion Criteria
- Evidence map is complete enough to explain why the output exists.
- Assumptions are explicit and bounded.
- Confidence level matches evidence quality.
- Next step and human touchpoint are named.
"""


def render_decision_boundaries(role: RoleContext) -> str:
    autonomy = ROLE_CLASS_RULES[role.role_class]['autonomy']
    return f"""# Decision Boundaries — {role.role} ({role.alias})

## Trusted to Do Autonomously
- {autonomy}
- Prepare draft outputs within the role scope.
- Flag evidence gaps, source conflicts, and missing approvals.

## Must Never Do Autonomously
- Final approval, signature, publication, payment authorization, legal commitment, or procurement award.
- Reclassify sensitive data downward without human decision.
- Override explicit monitor/compliance hold conditions.

## Human-in-the-Loop Requirements
- L3/L4 action or any externally impactful step
- Legal/fiscal/procurement/public-risk outputs
- Sensitive or restricted data handling questions
- Conflict between canonical sources

## Red-Flag Overrides
""" + '\n'.join(f"- {flag}" for flag in role.red_flags[:5]) + f"""

## Escalation Owner Rule
If the human owner, approver, or accountable officer cannot be named, stop autonomous progression and hand off to Winda or the role accountable in the local operating model.
"""


def render_reference_catalog(role: RoleContext) -> str:
    return f"""# Reference Catalog — {role.role} ({role.alias})

## Stable Reference Data to Maintain Here
- Canonical field definitions used by {role.role.lower()} work
- Entity lists, controlled vocabularies, and status codes
- Mapping tables between role inputs and required outputs
- Stable lookup values that are reused across cases

## Suggested Reference Tables
- request type -> output artifact
- action level -> approval owner
- confidence signal -> escalation action
- source type -> trust level

## Shared Reference Dependencies
- `../_shared-links/04-data-dictionaries` for common cross-role terms
- `../_shared-links/05-risk-and-compliance` for reusable trigger labels

## Maintenance Rule
Keep this folder factual and stable. Working assumptions, one-off calculations, or temporary notes belong in source or workflow folders, not here.
"""


def render_starter_outputs(role: RoleContext) -> str:
    samples = role.expected_artifacts[:3]
    return f"""# Starter Output Examples — {role.role} ({role.alias})

## Example 1 — Rapid Triage
- **Task shape:** short operational request in `{role.cluster}`
- **Expected artifact:** {samples[0] if samples else 'role-specific output'}
- **Output skeleton:**
  - summary
  - evidence_map
  - assumptions
  - confidence_status
  - red_flags
  - human_touchpoint
  - next_step

## Example 2 — Review / Challenge
- **Task shape:** user asks to check, validate, or compare
- **Expected artifact:** {samples[1] if len(samples) > 1 else samples[0] if samples else 'review note'}
- **What good looks like:** cites source basis, identifies gaps, states pass/hold/block, and names reviewer.

## Example 3 — Escalation-Ready Draft
- **Task shape:** evidence incomplete or approval path unclear
- **Expected artifact:** {samples[2] if len(samples) > 2 else 'escalation-ready memo'}
- **What good looks like:** states blocker, impact, missing owner, and exact next human action.

## Example Hygiene Rules
- Never present starter examples as issued official documents.
- Replace placeholders with institution-specific templates as soon as they exist.
- Keep at least one approved real-world exemplar here once production adoption begins.
"""


def render_quality_checklist(role: RoleContext) -> str:
    return f"""# Quality Checklist — {role.role} ({role.alias})

## Pre-Release Review Checklist
- [ ] Role fit is correct for the request.
- [ ] Sources are named, current enough, and classified.
- [ ] Output uses the required contract structure.
- [ ] Assumptions are explicit and bounded.
- [ ] Confidence is not inflated beyond the evidence quality.
- [ ] Human touchpoint is named for consequential action.

## Common Failure Modes
- Wrong role keeps the task instead of routing or escalating.
- Template language is used without source grounding.
- Sensitive/public-impact content is drafted without approval path.
- Evidence map is omitted or too vague to audit.
- Example output is mistaken for official approval.

## Red-Flag Patterns
""" + '\n'.join(f"- {flag}" for flag in role.red_flags[:6]) + f"""

## Reviewer Notes
- Prefer concise challenge notes over silent corrections.
- If you cannot explain why the output is safe, mark it low confidence and stop.
"""


def render_intake_guide(role: RoleContext) -> str:
    return f"""# Intake Guide — {role.role} ({role.alias})

## What New Knowledge Belongs Here
- New official documents directly used by {role.role.lower()}.
- Role-local SOP refinements and approved workflow notes.
- Approved templates and high-quality output exemplars.
- Stable reference tables needed repeatedly by this role.

## Minimum Intake Metadata
- document_title
- issuing_owner
- issue_date
- revision_or_version
- source_type
- classification
- role_relevance
- review_status

## Ingestion Steps
1. Put raw source material in the semantically correct folder.
2. Add provenance metadata using the templates already in this directory.
3. Update `source-map.md`, `policy-map.md`, or `artifact-catalog.md` when the new material changes how the role should work.
4. Move superseded material to `../09-archive` with a short reason.

## Do Not Ingest
- Unsourced copied text
- Personal notes without institutional value
- Drafts that have no owner or review path
- Sensitive data that should stay in a protected system instead of the repo
"""


def render_archive_rules(role: RoleContext) -> str:
    return f"""# Archive Rules — {role.role} ({role.alias})

## What Belongs in Archive
- Superseded templates and examples
- Expired policy extracts kept only for historical traceability
- Working notes no longer used by active SOPs
- Deprecated reference tables replaced by newer canonical versions

## Archive Procedure
- Preserve provenance and the reason for archival.
- Do not delete historical material if it is still needed for audit reconstruction.
- Prefer a short archive note naming replacement files or folders.

## Never Archive Without Replacement Signal
- The only active workflow map
- The only current policy interpretation note
- The only output example that proves role usability
"""


def render_shared_routing(contexts: list[RoleContext]) -> str:
    lines = ['# Role Routing Matrix', '', '## Core Routing Rules', '- Yayak is the default router and action-level gate.', '- Specialist roles execute within domain.', '- Monitor/compliance roles challenge unsupported or unsafe outputs.', '- Winda resolves unresolved conflict, missing approver paths, and blocked execution.']
    lines += ['', '## Role Class Summary']
    grouped: dict[str, list[str]] = {'router': [], 'specialist': [], 'monitor': [], 'escalation': []}
    for ctx in contexts:
        grouped[ctx.role_class].append(f"- {ctx.role} ({ctx.alias}) — `{ctx.cluster}` — {ctx.focus}")
    for key in ['router', 'specialist', 'monitor', 'escalation']:
        lines.append(f"### {ROLE_CLASS_RULES[key]['summary'].title()}")
        lines.extend(grouped[key])
    return '\n'.join(lines) + '\n'


def render_shared_regulations() -> str:
    return """# Regulatory Source Hierarchy

## Canonical Source Order
1. Issued laws, regulations, decrees, circulars, and formally approved internal policies
2. Approved SOPs and workflow instructions
3. Approved templates and signed exemplars
4. Working notes, draft mappings, and non-binding summaries

## Handling Conflicts
- Prefer the newest valid canonical source.
- If two canonical sources conflict, do not reconcile silently; escalate with evidence.
- Treat examples as formatting support, never as policy authority.
"""


def render_shared_sops() -> str:
    return """# Common SOP Primitives

## Reusable Flow Blocks
- intake -> classify -> validate source -> draft/review -> approve -> archive
- detect red flag -> hold -> escalate -> name human owner -> resume only after decision
- retrieve template -> populate with evidence -> review assumptions -> log output status

## Shared Control Points
- data classification check
- action-level check
- human-in-the-loop gate
- audit log completeness
"""


def render_shared_templates() -> str:
    return """# Global Artifact Patterns

## Shared Output Contract
- summary
- evidence_map
- assumptions
- confidence_status
- red_flags
- human_touchpoint
- next_step

## Template Notes
Use role-local templates first. Shared patterns are for structure consistency when role-local templates are absent or still immature.
"""


def render_shared_dictionary() -> str:
    return """# Common Data Dictionary

## Shared Terms
- action_level: operational impact level used to determine approval strictness
- evidence_map: list or narrative mapping from claim to supporting source
- human_touchpoint: named reviewer, approver, or accountable officer
- red_flag: condition that should reduce confidence or stop autonomous action
- trace_id: stable identifier used to reconnect decisions, outputs, and audit logs
"""


def render_shared_risks() -> str:
    return """# Risk and Compliance Trigger Matrix

## Immediate Hold Triggers
- missing canonical source for consequential action
- unclear human approver for L3/L4 work
- sensitive/restricted data handling uncertainty
- legal, fiscal, procurement, or public impact without review path
- unresolved contradiction between specialist and monitor roles

## Escalation Targets
- domain monitor/compliance role for challenge
- Winda for unresolved conflict or missing owner
- human authority for final decision
"""


def render_shared_audit() -> str:
    return """# Audit and Observability Contract

## Minimum Audit Expectations
- trace_id preserved across routing and handoff
- output status recorded: draft, review, hold, approved, archived
- source references are visible enough for reconstruction
- human reviewer / approver is named for consequential outputs

## Observability Notes
Good runtime behavior is explainable, replayable, and bounded. If a role cannot show its source basis or handoff point, treat the output as low confidence.
"""


def render_shared_outputs() -> str:
    return """# Golden Output Patterns

## Output Hallmarks
- concise summary first
- explicit evidence map
- clearly separated assumptions
- realistic confidence label
- visible red flags and human touchpoint
- actionable next step

## Anti-Pattern Warnings
- polished prose with no source basis
- confident tone hiding missing approval path
- examples mistaken for active institutional policy
"""


def render_knowledge_map(role: RoleContext) -> str:
    prompt_rel = f"prompts/roles/{role.skill_slug}.md"
    kb_rel = f"knowledge-base/{role.path}"
    return f"""# Knowledge Map

## Role Prompt
- `{prompt_rel}`

## Role Knowledge Folder
- `{kb_rel}`

## Shared Knowledge Links
- `{kb_rel}/_shared-links`

## Required Role Starter Artifacts
- Charter: `{kb_rel}/00-readme/role-charter.md`
- Source map: `{kb_rel}/01-source-documents/source-map.md`
- Policy map: `{kb_rel}/02-regulations-and-policies/policy-map.md`
- Artifact catalog: `{kb_rel}/03-templates-and-examples/artifact-catalog.md`
- Workflow map: `{kb_rel}/04-sop-and-workflows/workflow-map.md`
- Decision boundaries: `{kb_rel}/04-sop-and-workflows/decision-boundaries.md`
- Reference catalog: `{kb_rel}/05-reference-data/reference-catalog.md`
- Output examples: `{kb_rel}/06-output-samples/starter-output-examples.md`
- Review checklist: `{kb_rel}/07-review-notes/quality-checklist.md`
- Intake guide: `{kb_rel}/08-ingestion-ready/intake-guide.md`

## Suggested Reads by Need
- Role mandate and boundaries: `00-readme/role-charter.md` then `04-sop-and-workflows/decision-boundaries.md`
- Trusted sources: `01-source-documents/source-map.md` then `_shared-links/01-regulasi-umum`
- Workflow execution: `04-sop-and-workflows/workflow-map.md` then `_shared-links/02-sop-umum`
- Output shaping: `03-templates-and-examples/artifact-catalog.md` then `06-output-samples/starter-output-examples.md`
- Stable lookups: `05-reference-data/reference-catalog.md` and shared dictionaries if linked
- Review and escalation: `07-review-notes/quality-checklist.md`, risk/compliance links, and audit/observability links when present

## Retrieval Rule
Prefer role-specific starter knowledge first. Use shared knowledge for canonical cross-role rules, dictionaries, and golden control patterns. Escalate when local starter knowledge and shared canonical guidance conflict.
"""


def score_role(role_dir: Path) -> dict[str, Any]:
    checks = {
        'source_coverage': role_dir / '01-source-documents' / 'source-map.md',
        'sop_coverage': role_dir / '04-sop-and-workflows' / 'workflow-map.md',
        'template_coverage': role_dir / '03-templates-and-examples' / 'artifact-catalog.md',
        'output_example_coverage': role_dir / '06-output-samples' / 'starter-output-examples.md',
        'review_note_coverage': role_dir / '07-review-notes' / 'quality-checklist.md',
        'ingestion_readiness': role_dir / '08-ingestion-ready' / 'intake-guide.md',
        'escalation_clarity': role_dir / '04-sop-and-workflows' / 'decision-boundaries.md',
    }
    result: dict[str, Any] = {}
    scores = []
    for name, path in checks.items():
        if path.exists():
            text = path.read_text().strip()
            if len(text) > 1200:
                score = 4
                label = 'high-confidence'
            elif len(text) > 700:
                score = 3
                label = 'operational'
            elif len(text) > 250:
                score = 2
                label = 'usable'
            else:
                score = 1
                label = 'seed'
        else:
            score = 0
            label = 'seed'
        result[name] = {'score': score, 'label': label, 'present': path.exists()}
        scores.append(score)
    shared_links = role_dir / '_shared-links'
    quality = 4 if shared_links.exists() and all(link.exists() for link in shared_links.iterdir()) else 1
    result['shared_link_quality'] = {'score': quality, 'label': READINESS_ORDER[min(max(quality-1, 0), 3)], 'present': shared_links.exists()}
    avg = sum(scores + [quality]) / (len(scores) + 1)
    if avg >= 3.5:
        readiness = 'high-confidence'
    elif avg >= 2.5:
        readiness = 'operational'
    elif avg >= 1.5:
        readiness = 'usable'
    else:
        readiness = 'seed'
    missing = [name for name, meta in result.items() if not meta['present']]
    return {'dimensions': result, 'readiness': readiness, 'missing': missing, 'average_score': round(avg, 2)}


def write_file(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        existing = path.read_text()
        if existing == content:
            return False
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate starter knowledge artifacts for Gov-Agentic AI roles.')
    parser.add_argument('--check', action='store_true', help='Report what would be generated without writing files.')
    parser.add_argument('--force', action='store_true', help='Overwrite managed starter files.')
    args = parser.parse_args()

    contexts = build_contexts()
    writes = 0
    skipped = 0

    renderers = {
        'role_charter': render_role_charter,
        'source_map': render_source_map,
        'policy_map': render_policy_map,
        'artifact_catalog': render_artifact_catalog,
        'workflow_map': render_workflow_map,
        'decision_boundaries': render_decision_boundaries,
        'reference_catalog': render_reference_catalog,
        'starter_outputs': render_starter_outputs,
        'quality_checklist': render_quality_checklist,
        'intake_guide': render_intake_guide,
        'archive_rules': render_archive_rules,
    }

    for ctx in contexts:
        for rel, key in STARTER_FILES.items():
            path = ctx.kb_dir / rel
            content = renderers[key](ctx)
            if args.check:
                if not path.exists():
                    print(f'MISSING {path.relative_to(ROOT)}')
                continue
            changed = write_file(path, content, force=args.force or not path.exists())
            writes += int(changed)
            skipped += int(not changed)

        km_path = ctx.skill_dir / 'references' / 'knowledge-map.md'
        km_content = render_knowledge_map(ctx)
        if not args.check:
            changed = write_file(km_path, km_content, force=True)
            writes += int(changed)
            skipped += int(not changed)

    shared_content = {
        'shared_routing': render_shared_routing(contexts),
        'shared_regulations': render_shared_regulations(),
        'shared_sops': render_shared_sops(),
        'shared_templates': render_shared_templates(),
        'shared_dictionary': render_shared_dictionary(),
        'shared_risks': render_shared_risks(),
        'shared_audit': render_shared_audit(),
        'shared_outputs': render_shared_outputs(),
    }
    for rel, key in SHARED_FILES.items():
        path = KB_ROOT / '_shared' / rel
        if args.check:
            if not path.exists():
                print(f'MISSING {path.relative_to(ROOT)}')
            continue
        changed = write_file(path, shared_content[key], force=True)
        writes += int(changed)
        skipped += int(not changed)

    report = {
        'version': 'v1.0',
        'generated_by': 'scripts/generate_role_knowledge.py',
        'role_count': len(contexts),
        'roles': [],
    }
    for ctx in contexts:
        score = score_role(ctx.kb_dir)
        report['roles'].append({
            'path': ctx.path,
            'cluster': ctx.cluster,
            'role': ctx.role,
            'alias': ctx.alias,
            'role_class': ctx.role_class,
            'readiness': score['readiness'],
            'average_score': score['average_score'],
            'missing': score['missing'],
            'dimensions': score['dimensions'],
        })
    report['summary'] = {
        'seed': sum(1 for item in report['roles'] if item['readiness'] == 'seed'),
        'usable': sum(1 for item in report['roles'] if item['readiness'] == 'usable'),
        'operational': sum(1 for item in report['roles'] if item['readiness'] == 'operational'),
        'high_confidence': sum(1 for item in report['roles'] if item['readiness'] == 'high-confidence'),
    }

    if args.check:
        print(json.dumps(report['summary'], indent=2))
        return 0

    QUALITY_MANIFEST.write_text(json.dumps(report, indent=2) + '\n')
    print(f'generated_roles={len(contexts)}')
    print(f'files_written={writes}')
    print(f'files_skipped={skipped}')
    print(f'quality_manifest={QUALITY_MANIFEST.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
