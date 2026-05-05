#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / 'configs'

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', text.lower()).strip()


def load_registry() -> dict[str, Any]:
    return load_json(CONFIGS / 'role_registry.json')


def index_roles(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {role['role_slug']: role for role in registry['roles']}


def load_routing_policy(registry: dict[str, Any]) -> dict[str, Any]:
    return registry.get('routing_policy', {})


def detect_intent(text: str, routing_policy: dict[str, Any]) -> str:
    intent_detection = routing_policy.get('intent_detection', {})
    keyword_rules = intent_detection.get('keyword_rules', {})
    default_intent = intent_detection.get('default_intent', 'route-intake')
    scores: dict[str, int] = {}
    for intent, keywords in keyword_rules.items():
        scores[intent] = sum(2 if kw in text else 0 for kw in keywords)
    if not scores:
        return default_intent
    best = max(scores.items(), key=lambda item: item[1])
    return best[0] if best[1] > 0 else default_intent


def detect_action_level(text: str, routing_policy: dict[str, Any]) -> str:
    policy = routing_policy.get('action_level_detection', {})
    keyword_rules = policy.get('keyword_rules', {})
    for level in ['L4', 'L3', 'L2', 'L1', 'L0']:
        if any(kw in text for kw in keyword_rules.get(level, [])):
            return level
    return policy.get('default_action_level', 'L2')


def detect_sensitive(text: str, routing_policy: dict[str, Any]) -> bool:
    hints = routing_policy.get('sensitivity_detection', {}).get('keyword_rules', [])
    return any(h in text for h in hints)


def detect_material_impact(text: str, routing_policy: dict[str, Any]) -> bool:
    hints = routing_policy.get('impact_detection', {}).get('keyword_rules', [])
    return any(h in text for h in hints)


def build_trace_id(text: str) -> str:
    return 'trace-' + hashlib.sha1(text.encode()).hexdigest()[:12]


def infer_work_state(intent: str, action_level: str, evidence_complete: bool, approval_owner_known: bool, routing_policy: dict[str, Any]) -> tuple[str, str]:
    policy = routing_policy.get('work_state_policy', {})
    review_intents = set(policy.get('review_intents', []))
    archive_intents = set(policy.get('archive_intents', []))
    draft_intents = set(policy.get('draft_intents', []))
    hold_threshold = policy.get('hold_when_action_level_at_least', 'L3')
    if intent == 'route-intake':
        return 'classified', policy.get('draft_document_status', 'draft')
    if not evidence_complete:
        return 'intake-check', policy.get('draft_document_status', 'draft')
    if intent in review_intents:
        return 'reviewing', policy.get('review_document_status', 'review')
    if intent in archive_intents:
        return 'reviewing', policy.get('review_document_status', 'review')
    if action_level in {hold_threshold, 'L4'} and approval_owner_known:
        return policy.get('approval_required_work_state', 'awaiting-approval'), policy.get('review_document_status', 'review')
    if action_level in {hold_threshold, 'L4'} and not approval_owner_known:
        return 'blocked', 'hold'
    if intent in draft_intents:
        return 'drafting', policy.get('draft_document_status', 'draft')
    return 'drafting', policy.get('draft_document_status', 'draft')


def score_role(text: str, role: dict[str, Any]) -> int:
    score = 0
    alias = (role.get('alias') or '').lower()
    role_name = (role.get('role') or '').lower()
    cluster = (role.get('cluster') or '').lower()
    focus = ((role.get('persona') or {}).get('focus') or '').lower()
    triggers = [str(t).lower() for t in role.get('trigger_keywords', [])]
    use_cases = [str(u).lower().replace('_', ' ') for u in ((role.get('orchestration') or {}).get('primary_use_cases', []))]

    if alias and alias in text:
        score += 6
    if role_name and role_name in text:
        score += 6
    if cluster and cluster in text:
        score += 2
    if focus:
        score += sum(1 for token in [part.strip() for part in re.split(r'[,/+]', focus) if part.strip()] if token in text)
    score += sum(2 for kw in triggers if kw and kw in text)
    score += sum(2 for uc in use_cases if uc and uc in text)
    return score


def detect_role(text: str, roles_by_slug: dict[str, dict[str, Any]]) -> str:
    ranked = sorted(((score_role(text, role), slug) for slug, role in roles_by_slug.items()), reverse=True)
    best_score, best_slug = ranked[0]
    return best_slug if best_score > 0 else 'top-layer__gov-ai_yayak'


def required_evidence_for(role: dict[str, Any], intent: str) -> list[str]:
    shared = ((role.get('contracts') or {}).get('shared_input_contract') or [])
    specific = ((role.get('contracts') or {}).get('role_specific_input_contract') or [])
    mapped_shared = []
    mapping = {
        'task_summary': 'task objective',
        'available_evidence': 'source provenance',
        'data_classification': 'data classification',
        'action_level': 'action level',
        'human_owner_or_reviewer': 'approval owner',
    }
    for item in shared:
        mapped_shared.append(mapping.get(item, item.replace('_', ' ')))
    out = []
    for item in mapped_shared + [i.replace('_', ' ') for i in specific[:4]]:
        if item not in out:
            out.append(item)
    if intent.startswith('review-') and 'review criteria' not in out:
        out.append('review criteria')
    return out or ['task objective', 'source provenance']


def role_class_of(role: dict[str, Any]) -> str:
    return ((role.get('authority') or {}).get('role_class')) or 'specialist'


def allowed_for_context(role: dict[str, Any], action_level: str, sensitive: bool) -> bool:
    authority = role.get('authority') or {}
    allowed_levels = authority.get('action_levels_allowed') or ['L0', 'L1']
    allowed_classes = [c.lower() for c in (authority.get('data_classification_allowed') or ['public', 'internal'])]
    if action_level not in allowed_levels:
        return False
    if sensitive and 'restricted-with-human-review' not in allowed_classes:
        return False
    return True


def resolve_next_role(current_role_slug: str, intent: str, roles_by_slug: dict[str, dict[str, Any]], action_level: str, sensitive: bool, routing_policy: dict[str, Any]) -> str | None:
    current = roles_by_slug.get(current_role_slug)
    if not current:
        return None
    orchestration = current.get('orchestration') or {}
    clusters = orchestration.get('handoff_targets_by_cluster') or []
    role_classes = orchestration.get('handoff_role_classes') or []
    target_class_set = set(str(x).lower() for x in role_classes)

    preferred_slugs = list(routing_policy.get('intent_primary_candidates', {}).get(intent, []))

    candidates = []
    for slug, role in roles_by_slug.items():
        if slug == current_role_slug:
            continue
        if role.get('cluster') not in clusters and slug not in preferred_slugs:
            continue
        if target_class_set and role_class_of(role).lower() not in target_class_set and slug not in preferred_slugs:
            continue
        if not allowed_for_context(role, action_level, sensitive):
            continue
        candidates.append(slug)

    for preferred in preferred_slugs:
        if preferred in candidates:
            return preferred
        if preferred in roles_by_slug and allowed_for_context(roles_by_slug[preferred], action_level, sensitive):
            return preferred

    return candidates[0] if candidates else None


def gate_decision(action_level: str, evidence_complete: bool, approval_owner_known: bool, has_material_impact: bool, current_role: dict[str, Any]) -> tuple[str, str | None, str | None]:
    role_class = role_class_of(current_role)
    if not evidence_complete:
        return 'HOLD', None, 'missing evidence basis'
    if action_level == 'L4' and not approval_owner_known:
        return 'ESCALATE_TO', 'bottom-gate__bot-eskalasi_winda', 'approval owner unclear for L4'
    if action_level in {'L3', 'L4'} and has_material_impact:
        return 'REVIEW_NEEDED', None, 'human approval required for consequential action'
    if role_class == 'monitor' and has_material_impact:
        return 'REVIEW_NEEDED', None, 'monitor finding should be acknowledged by human owner'
    return 'PROCEED', None, None


def build_decision(payload: dict[str, Any]) -> dict[str, Any]:
    rules = load_json(CONFIGS / 'government_logic_rules.json')
    registry = load_registry()
    roles_by_slug = index_roles(registry)
    routing_policy = load_routing_policy(registry)

    text = normalize(payload.get('request_text', ''))
    role_slug = payload.get('current_role_slug') or 'top-layer__gov-ai_yayak'
    role = roles_by_slug.get(role_slug, {})

    intent = payload.get('intent_class') or detect_intent(text, routing_policy)
    action_level = payload.get('action_level') or detect_action_level(text, routing_policy)
    evidence_complete = bool(payload.get('evidence_complete', False))
    approval_owner_known = bool(payload.get('approval_owner_known', False))
    has_material_impact = bool(payload.get('material_impact', detect_material_impact(text, routing_policy)))
    sensitive = bool(payload.get('sensitive', detect_sensitive(text, routing_policy)))

    work_state, document_status = infer_work_state(intent, action_level, evidence_complete, approval_owner_known, routing_policy)
    next_owner = payload.get('next_owner_role') or resolve_next_role(role_slug, intent, roles_by_slug, action_level, sensitive, routing_policy)
    required_evidence = payload.get('required_evidence') or required_evidence_for(role, intent)

    authority = role.get('authority') or {}
    approval_gate = None if action_level in {'L0', 'L1'} else authority.get('approval_owner_hint', 'human accountable owner')
    stop_condition = None

    decision, escalate_to, reason = gate_decision(action_level, evidence_complete, approval_owner_known, has_material_impact or sensitive, role)
    if decision == 'HOLD':
        work_state = 'blocked'
        document_status = 'hold'
        stop_condition = reason
    elif decision == 'ESCALATE_TO':
        work_state = 'escalated'
        document_status = 'hold'
        stop_condition = reason
        next_owner = escalate_to
    elif decision == 'REVIEW_NEEDED' and work_state not in {'awaiting-approval', 'reviewing'}:
        work_state = 'awaiting-approval'
        document_status = 'review'
        stop_condition = reason

    trace_id = payload.get('trace_id') or build_trace_id(text)
    output = {
        'trace_id': trace_id,
        'intent_class': intent,
        'work_state': work_state,
        'current_owner_role': role_slug,
        'next_owner_role': next_owner,
        'action_level': action_level,
        'document_status': document_status,
        'required_evidence': required_evidence,
        'approval_gate': approval_gate,
        'stop_condition': stop_condition,
        'human_touchpoint_required': action_level in {'L3', 'L4'} or has_material_impact or sensitive,
        'notes': payload.get('notes', ''),
        'decision_gate': decision,
        'decision_reason': reason,
        'government_logic_version': rules['version'],
    }
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description='Registry-native government decision engine for Gov-Agentic AI.')
    parser.add_argument('--input-json', help='Path to input JSON payload')
    parser.add_argument('--request-text', help='Raw request text if not using --input-json')
    parser.add_argument('--current-role-slug', help='Optional current role slug')
    parser.add_argument('--evidence-complete', action='store_true', help='Mark evidence as complete')
    parser.add_argument('--approval-owner-known', action='store_true', help='Mark approval owner as known')
    parser.add_argument('--material-impact', action='store_true', help='Mark the request as materially impactful')
    parser.add_argument('--sensitive', action='store_true', help='Mark the request as sensitive')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON')
    args = parser.parse_args()

    if args.input_json:
        payload = load_json(Path(args.input_json))
    else:
        payload = {
            'request_text': args.request_text or '',
            'current_role_slug': args.current_role_slug,
            'evidence_complete': args.evidence_complete,
            'approval_owner_known': args.approval_owner_known,
            'material_impact': args.material_impact,
            'sensitive': args.sensitive,
        }
    if not payload.get('request_text'):
        print('ERROR: request_text is required', file=sys.stderr)
        return 2
    decision = build_decision(payload)
    print(json.dumps(decision, indent=2 if args.pretty else None, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
