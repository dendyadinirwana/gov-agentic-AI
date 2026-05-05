#!/usr/bin/env python3
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
CONTRACT_VERSION = "a2a.v1"

WORKFLOW_INTENTS = {
    "route-intake","check-completeness","draft-formal-artifact","review-compliance","review-legal-risk",
    "review-budget-fit","review-specification-neutrality","prepare-disposition","prepare-archive-record",
    "explain-policy-for-public","summarize-meeting-record","request-approval-path","escalate-blocker"
}
WORKFLOW_STATES = {"received","classified","intake-check","drafting","reviewing","awaiting-approval","approved","archived","blocked","escalated"}
DOC_STATUSES = {"draft","review","hold","approved","archived"}
ACTION_LEVELS = {"L0","L1","L2","L3","L4"}
DECISION_GATES = {"PROCEED","REVIEW_NEEDED","HOLD","ESCALATE_TO"}
RESPONSE_STATUS = {"completed","needs_review","blocked","failed"}
CONFIDENCE = {"low","medium","high"}
AUDIT_TYPES = {
    "handoff_created",
    "role_response_recorded",
    "workflow_terminalized",
    "governance_gate_triggered",
    "human_touchpoint_required",
    "fallback_used",
    "runtime_failed",
    "runtime_timeout",
    "review_returned",
}
AUDIT_SEVERITIES = {"info", "warning", "critical"}
AUDIT_RETENTION_CLASSES = {"ephemeral", "operational_record", "governance_record", "incident_record"}
AUDIT_COMPLIANCE_CLASSES = {"standard", "governance_control", "human_approval", "runtime_incident"}
AUDIT_RESPONSE_POLICIES = {"log_only", "review_required", "ack_required", "escalate_required"}
AUDIT_POLICY_BY_TYPE = {
    "handoff_created": {
        "severity": "info",
        "retention_class": "operational_record",
        "compliance_class": "standard",
        "response_policy": "log_only",
    },
    "role_response_recorded": {
        "severity": "info",
        "retention_class": "operational_record",
        "compliance_class": "standard",
        "response_policy": "log_only",
    },
    "workflow_terminalized": {
        "severity": "info",
        "retention_class": "governance_record",
        "compliance_class": "standard",
        "response_policy": "log_only",
    },
    "governance_gate_triggered": {
        "severity": "warning",
        "retention_class": "governance_record",
        "compliance_class": "governance_control",
        "response_policy": "review_required",
    },
    "human_touchpoint_required": {
        "severity": "warning",
        "retention_class": "governance_record",
        "compliance_class": "human_approval",
        "response_policy": "ack_required",
    },
    "fallback_used": {
        "severity": "warning",
        "retention_class": "governance_record",
        "compliance_class": "governance_control",
        "response_policy": "review_required",
    },
    "review_returned": {
        "severity": "warning",
        "retention_class": "governance_record",
        "compliance_class": "human_approval",
        "response_policy": "review_required",
    },
    "runtime_failed": {
        "severity": "critical",
        "retention_class": "incident_record",
        "compliance_class": "runtime_incident",
        "response_policy": "escalate_required",
    },
    "runtime_timeout": {
        "severity": "critical",
        "retention_class": "incident_record",
        "compliance_class": "runtime_incident",
        "response_policy": "escalate_required",
    },
}
AUDIT_SEVERITY_BY_TYPE = {event_type: policy["severity"] for event_type, policy in AUDIT_POLICY_BY_TYPE.items()}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_iso(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def validate_workflow_state(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ["trace_id","intent_class","work_state","current_owner_role","action_level","document_status","human_touchpoint_required"]
    for key in required:
        if key not in state:
            errors.append(f"workflow_state missing key: {key}")
    if state.get("intent_class") not in WORKFLOW_INTENTS:
        errors.append(f"invalid workflow_state.intent_class: {state.get('intent_class')}")
    if state.get("work_state") not in WORKFLOW_STATES:
        errors.append(f"invalid workflow_state.work_state: {state.get('work_state')}")
    if state.get("document_status") not in DOC_STATUSES:
        errors.append(f"invalid workflow_state.document_status: {state.get('document_status')}")
    if state.get("action_level") not in ACTION_LEVELS:
        errors.append(f"invalid workflow_state.action_level: {state.get('action_level')}")
    if not isinstance(state.get("human_touchpoint_required"), bool):
        errors.append("workflow_state.human_touchpoint_required must be boolean")
    return errors


def validate_handoff(handoff: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ["contract_version","trace_id","handoff_id","from_role","to_role","intent_class","task_summary","action_level","workflow_state","payload","governance","audit"]:
        if key not in handoff:
            errors.append(f"handoff missing key: {key}")
    if handoff.get("contract_version") != CONTRACT_VERSION:
        errors.append("handoff.contract_version must be a2a.v1")
    if handoff.get("action_level") not in ACTION_LEVELS:
        errors.append(f"invalid handoff.action_level: {handoff.get('action_level')}")
    if isinstance(handoff.get("workflow_state"), dict):
        errors.extend(validate_workflow_state(handoff["workflow_state"]))
    else:
        errors.append("handoff.workflow_state must be object")
    payload = handoff.get("payload")
    if not isinstance(payload, dict):
        errors.append("handoff.payload must be object")
    else:
        if not payload.get("request_text"):
            errors.append("handoff.payload.request_text is required")
        if not isinstance(payload.get("evidence_sources", []), list):
            errors.append("handoff.payload.evidence_sources must be array")
        if not isinstance(payload.get("assumptions", []), list):
            errors.append("handoff.payload.assumptions must be array")
    gov = handoff.get("governance")
    if not isinstance(gov, dict):
        errors.append("handoff.governance must be object")
    else:
        if gov.get("decision_gate") not in DECISION_GATES:
            errors.append(f"invalid handoff.governance.decision_gate: {gov.get('decision_gate')}")
        if not isinstance(gov.get("human_touchpoint_required"), bool):
            errors.append("handoff.governance.human_touchpoint_required must be boolean")
    audit = handoff.get("audit")
    if not isinstance(audit, dict):
        errors.append("handoff.audit must be object")
    else:
        if not _is_iso(str(audit.get("created_at", ""))):
            errors.append("handoff.audit.created_at must be ISO timestamp")
        if not isinstance(audit.get("sequence"), int):
            errors.append("handoff.audit.sequence must be integer")
    return errors


def validate_response(response: dict[str, Any], handoff: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    for key in ["contract_version","trace_id","response_id","role_slug","status","summary","evidence_map","assumptions","confidence","red_flags","human_touchpoint","next_step","audit"]:
        if key not in response:
            errors.append(f"response missing key: {key}")
    if response.get("contract_version") != CONTRACT_VERSION:
        errors.append("response.contract_version must be a2a.v1")
    if response.get("status") not in RESPONSE_STATUS:
        errors.append(f"invalid response.status: {response.get('status')}")
    if response.get("confidence") not in CONFIDENCE:
        errors.append(f"invalid response.confidence: {response.get('confidence')}")
    if not isinstance(response.get("evidence_map"), list):
        errors.append("response.evidence_map must be array")
    if not isinstance(response.get("assumptions"), list):
        errors.append("response.assumptions must be array")
    if not isinstance(response.get("red_flags"), list):
        errors.append("response.red_flags must be array")
    human = response.get("human_touchpoint")
    if not isinstance(human, dict) or not isinstance(human.get("required"), bool) or not isinstance(human.get("reason"), str):
        errors.append("response.human_touchpoint must contain required:boolean and reason:string")
    audit = response.get("audit")
    if not isinstance(audit, dict):
        errors.append("response.audit must be object")
    else:
        if not _is_iso(str(audit.get("handled_at", ""))):
            errors.append("response.audit.handled_at must be ISO timestamp")
        if not audit.get("handled_by"):
            errors.append("response.audit.handled_by is required")
        if not audit.get("adapter_mode"):
            errors.append("response.audit.adapter_mode is required")
    if handoff:
        if response.get("trace_id") != handoff.get("trace_id"):
            errors.append("response.trace_id must match handoff.trace_id")
        if response.get("role_slug") != handoff.get("to_role"):
            errors.append("response.role_slug must match handoff.to_role")
    return errors


def validate_terminal_state(terminal: dict[str, Any], trace_id: str | None = None) -> list[str]:
    errors: list[str] = []
    for key in ["contract_version","trace_id","status","summary","workflow_state"]:
        if key not in terminal:
            errors.append(f"terminal_state missing key: {key}")
    if terminal.get("contract_version") != CONTRACT_VERSION:
        errors.append("terminal_state.contract_version must be a2a.v1")
    if terminal.get("status") not in RESPONSE_STATUS:
        errors.append(f"invalid terminal_state.status: {terminal.get('status')}")
    if isinstance(terminal.get("workflow_state"), dict):
        errors.extend(validate_workflow_state(terminal["workflow_state"]))
    else:
        errors.append("terminal_state.workflow_state must be object")
    if trace_id and terminal.get("trace_id") != trace_id:
        errors.append("terminal_state.trace_id must match workflow trace")
    return errors


def validate_audit_event(event: dict[str, Any], trace_id: str | None = None) -> list[str]:
    errors: list[str] = []
    for key in ["contract_version","trace_id","event_id","event_type","created_at","actor_role","payload_ref","severity","retention_class","compliance_class","response_policy"]:
        if key not in event:
            errors.append(f"audit_event missing key: {key}")
    if event.get("contract_version") != CONTRACT_VERSION:
        errors.append("audit_event.contract_version must be a2a.v1")
    if event.get("event_type") not in AUDIT_TYPES:
        errors.append(f"invalid audit_event.event_type: {event.get('event_type')}")
    if event.get("severity") not in AUDIT_SEVERITIES:
        errors.append(f"invalid audit_event.severity: {event.get('severity')}")
    if event.get("retention_class") not in AUDIT_RETENTION_CLASSES:
        errors.append(f"invalid audit_event.retention_class: {event.get('retention_class')}")
    if event.get("compliance_class") not in AUDIT_COMPLIANCE_CLASSES:
        errors.append(f"invalid audit_event.compliance_class: {event.get('compliance_class')}")
    if event.get("response_policy") not in AUDIT_RESPONSE_POLICIES:
        errors.append(f"invalid audit_event.response_policy: {event.get('response_policy')}")
    expected_policy = AUDIT_POLICY_BY_TYPE.get(event.get("event_type"))
    if expected_policy:
        if event.get("severity") != expected_policy["severity"]:
            errors.append(f"audit_event.severity must be {expected_policy['severity']} for event_type {event.get('event_type')}")
        if event.get("retention_class") != expected_policy["retention_class"]:
            errors.append(f"audit_event.retention_class must be {expected_policy['retention_class']} for event_type {event.get('event_type')}")
        if event.get("compliance_class") != expected_policy["compliance_class"]:
            errors.append(f"audit_event.compliance_class must be {expected_policy['compliance_class']} for event_type {event.get('event_type')}")
        if event.get("response_policy") != expected_policy["response_policy"]:
            errors.append(f"audit_event.response_policy must be {expected_policy['response_policy']} for event_type {event.get('event_type')}")
    if not _is_iso(str(event.get("created_at", ""))):
        errors.append("audit_event.created_at must be ISO timestamp")
    if trace_id and event.get("trace_id") != trace_id:
        errors.append("audit_event.trace_id must match workflow trace")
    return errors
