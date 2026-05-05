#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from a2a_contracts import AUDIT_POLICY_BY_TYPE, validate_audit_event, validate_handoff, validate_response, validate_terminal_state
from government_decision_engine import build_decision
from local_retriever import retrieve
from role_runner import build_role_runner

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / "configs"
CONTRACT_VERSION = "a2a.v1"
ROLE_YAYAK = "top-layer__gov-ai_yayak"
ROLE_ALFIAN = "komunikasi-dan-dokumen__penulis-naskah_alfian"
ROLE_EDI = "kebijakan-dan-hukum__monitor-kepatuhan-hukum_edi"
ROLE_WINDA = "bottom-gate__bot-eskalasi_winda"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_role_registry() -> dict[str, Any]:
    return load_json(CONFIGS / "role_registry.json")


def index_roles(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {role["role_slug"]: role for role in registry["roles"]}


def load_routing_policy(registry: dict[str, Any]) -> dict[str, Any]:
    return registry.get("routing_policy", {})


def build_audit_event(trace_id: str, event_type: str, actor_role: str, payload_ref: str, notes: str | None = None) -> dict[str, Any]:
    policy = AUDIT_POLICY_BY_TYPE[event_type]
    event = {
        "contract_version": CONTRACT_VERSION,
        "trace_id": trace_id,
        "event_id": f"event-{uuid.uuid4().hex[:12]}",
        "event_type": event_type,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "actor_role": actor_role,
        "payload_ref": payload_ref,
        "severity": policy["severity"],
        "retention_class": policy["retention_class"],
        "compliance_class": policy["compliance_class"],
        "response_policy": policy["response_policy"],
        "notes": notes,
    }
    errors = validate_audit_event(event, trace_id)
    if errors:
        raise ValueError("invalid audit event: " + "; ".join(errors))
    return event


def build_handoff(*, trace_id: str, from_role: str, to_role: str, sequence: int, task_summary: str, workflow_state: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    handoff = {
        "contract_version": CONTRACT_VERSION,
        "trace_id": trace_id,
        "handoff_id": f"handoff-{uuid.uuid4().hex[:12]}",
        "from_role": from_role,
        "to_role": to_role,
        "intent_class": workflow_state["intent_class"],
        "task_summary": task_summary,
        "action_level": workflow_state["action_level"],
        "workflow_state": workflow_state,
        "payload": payload,
        "governance": {
            "decision_gate": workflow_state["decision_gate"],
            "decision_reason": workflow_state.get("decision_reason"),
            "human_touchpoint_required": workflow_state["human_touchpoint_required"],
            "approval_gate": workflow_state.get("approval_gate"),
            "stop_condition": workflow_state.get("stop_condition"),
        },
        "audit": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": from_role,
            "sequence": sequence,
        },
    }
    errors = validate_handoff(handoff)
    if errors:
        raise ValueError("invalid handoff: " + "; ".join(errors))
    return handoff


def resolve_primary_role(intent_class: str, workflow_state: dict[str, Any], roles_by_slug: dict[str, dict[str, Any]], routing_policy: dict[str, Any]) -> str:
    if workflow_state.get("next_owner_role") in roles_by_slug:
        return workflow_state["next_owner_role"]
    primary_candidates = routing_policy.get("intent_primary_candidates", {}).get(intent_class, [])
    for candidate in primary_candidates:
        if candidate in roles_by_slug:
            return candidate
    default_router = routing_policy.get("default_router_role", ROLE_YAYAK)
    return ROLE_ALFIAN if intent_class == "draft-formal-artifact" and ROLE_ALFIAN in roles_by_slug else default_router


def resolve_review_role(primary_role: str, intent_class: str, roles_by_slug: dict[str, dict[str, Any]], routing_policy: dict[str, Any]) -> str | None:
    if primary_role == ROLE_WINDA or intent_class.startswith("review-"):
        return None
    primary = roles_by_slug.get(primary_role, {})
    cluster = primary.get("cluster")
    candidate = routing_policy.get("review_role_by_cluster", {}).get(cluster)
    if candidate and candidate != primary_role and candidate in roles_by_slug:
        return candidate
    default_review = routing_policy.get("default_review_role", ROLE_EDI)
    if primary_role != default_review and default_review in roles_by_slug:
        return default_review
    return None


def task_summary_for(role_slug: str, roles_by_slug: dict[str, dict[str, Any]], phase: str) -> str:
    role = roles_by_slug.get(role_slug, {})
    role_name = role.get("role", role_slug)
    role_class = (role.get("authority") or {}).get("role_class", "specialist")
    use_cases = (role.get("orchestration") or {}).get("primary_use_cases", [])
    if phase == "primary":
        focus = use_cases[0] if use_cases else "role-specific work"
        return f"Jalankan peran {role_name} untuk menangani pekerjaan utama: {focus}."
    if phase == "review":
        if role_class == "monitor":
            return f"Tinjau hasil sebelumnya dengan peran {role_name} dan identifikasi gap kontrol, kepatuhan, atau risiko material."
        return f"Lakukan review lanjutan dengan peran {role_name} berdasarkan artefak dari langkah sebelumnya."
    return f"Jalankan peran {role_name}."


def emit_response_audit_events(trace_id: str, handoff: dict[str, Any], response: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    role_slug = response["role_slug"]
    events.append(build_audit_event(trace_id, "role_response_recorded", role_slug, response["response_id"], response["status"]))

    hints = ((response.get("adapter_execution") or {}).get("audit_hints") or {})
    if hints.get("fallback_used"):
        notes = f"fallback {hints.get('fallback_from')} -> {hints.get('fallback_to')}"
        events.append(build_audit_event(trace_id, "fallback_used", role_slug, response["response_id"], notes))
    if hints.get("runtime_failed"):
        events.append(build_audit_event(trace_id, "runtime_failed", role_slug, response["response_id"], response.get("summary")))
    if hints.get("runtime_timeout"):
        events.append(build_audit_event(trace_id, "runtime_timeout", role_slug, response["response_id"], response.get("summary")))
    if hints.get("review_returned"):
        events.append(build_audit_event(trace_id, "review_returned", role_slug, response["response_id"], response.get("next_step")))

    human_required = bool(hints.get("human_touchpoint_required")) or bool((response.get("human_touchpoint") or {}).get("required"))
    if human_required:
        events.append(build_audit_event(trace_id, "human_touchpoint_required", role_slug, response["response_id"], (response.get("human_touchpoint") or {}).get("reason")))
    return events


def retrieval_payload(request: dict[str, Any], workflow_state: dict[str, Any]) -> dict[str, Any]:
    retrieval_required = bool(request.get("retrieval_required"))
    retrieval_result = retrieve(request.get("request_text", ""), workflow_state.get("intent_class")) if retrieval_required else {"provider": "disabled", "query_terms": [], "hits": []}
    evidence_sources = list(request.get("evidence_sources", []))
    for hit in retrieval_result.get("hits", []):
        label = hit.get("title") or hit.get("source_id")
        if label and label not in evidence_sources:
            evidence_sources.append(label)
    return {
        "required": retrieval_required,
        "provider": retrieval_result.get("provider", "disabled"),
        "query_terms": retrieval_result.get("query_terms", []),
        "hits": retrieval_result.get("hits", []),
        "evidence_sources": evidence_sources,
    }


def build_terminal_state(trace_id: str, workflow_state: dict[str, Any], steps: list[dict[str, Any]], roles_by_slug: dict[str, dict[str, Any]], retrieval: dict[str, Any]) -> dict[str, Any]:
    latest = steps[-1]["response"] if steps else None
    findings: list[str] = []
    path: list[str] = []
    for step in steps:
        findings.extend(step["response"].get("red_flags", []))
        role_slug = step["handoff"]["to_role"]
        role_name = roles_by_slug.get(role_slug, {}).get("alias") or roles_by_slug.get(role_slug, {}).get("role") or role_slug
        path.append(role_name)
    summary = f"Yayak mengorkestrasi alur ke {' → '.join(path)} lalu menyusun ringkasan akhir." if path else "Yayak menahan workflow karena governance gate."
    terminal = {
        "contract_version": CONTRACT_VERSION,
        "trace_id": trace_id,
        "status": latest["status"] if latest else "blocked",
        "final_status": latest["status"] if latest else "blocked",
        "summary": summary,
        "workflow_state": workflow_state,
        "recommended_next_step": latest["next_step"] if latest else "Lengkapi evidence dan ulangi orkestrasi.",
        "red_flags": findings,
        "final_artifact": steps[0]["response"].get("artifact") if steps else None,
        "execution_path": path,
        "step_count": len(steps),
        "orchestrator": ROLE_YAYAK,
        "retrieval": {
            "required": retrieval.get("required", False),
            "provider": retrieval.get("provider", "disabled"),
            "query_terms": retrieval.get("query_terms", []),
            "hit_count": len(retrieval.get("hits", [])),
            "sources": [
                {
                    "source_id": hit.get("source_id"),
                    "title": hit.get("title"),
                    "owner": hit.get("owner"),
                    "uri": hit.get("uri"),
                }
                for hit in retrieval.get("hits", [])
            ],
        },
    }
    errors = validate_terminal_state(terminal, trace_id)
    if errors:
        raise ValueError("invalid terminal state: " + "; ".join(errors))
    return terminal


def main() -> int:
    parser = argparse.ArgumentParser(description="Registry-driven A2A orchestrator for Gov-Agentic AI")
    parser.add_argument("--input-json", required=True, help="Path to orchestrator request payload")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print output")
    args = parser.parse_args()

    registry = load_role_registry()
    roles_by_slug = index_roles(registry)
    routing_policy = load_routing_policy(registry)

    runtime_config = load_json(CONFIGS / "runtime.generated.json") if (CONFIGS / "runtime.generated.json").exists() else {"runtime_target": "generic"}
    runner = build_role_runner(runtime_config.get("runtime_target", "generic"))

    request = load_json(Path(args.input_json))
    request_text = request.get("request_text", "")
    if not request_text:
        print("ERROR: request_text is required")
        return 2

    workflow_state = build_decision({
        "request_text": request_text,
        "current_role_slug": ROLE_YAYAK,
        "evidence_complete": request.get("evidence_complete", False),
        "approval_owner_known": request.get("approval_owner_known", False),
        "material_impact": request.get("material_impact", False),
        "sensitive": request.get("sensitive", False),
        "intent_class": request.get("intent_class"),
        "action_level": request.get("action_level"),
    })

    trace_id = workflow_state["trace_id"]
    audit_events: list[dict[str, Any]] = []

    if workflow_state["decision_gate"] == "HOLD":
        audit_events.append(build_audit_event(trace_id, "governance_gate_triggered", ROLE_YAYAK, trace_id, workflow_state.get("decision_reason")))
        if workflow_state.get("human_touchpoint_required"):
            audit_events.append(build_audit_event(trace_id, "human_touchpoint_required", ROLE_YAYAK, trace_id, workflow_state.get("approval_gate")))
        final = build_terminal_state(trace_id, workflow_state, [], roles_by_slug, {"required": False, "provider": "disabled", "query_terms": [], "hits": []})
        audit_events.append(build_audit_event(trace_id, "workflow_terminalized", ROLE_YAYAK, "final", final["summary"]))
        output = {"contract_version": CONTRACT_VERSION, "trace_id": trace_id, "workflow_state": workflow_state, "steps": [], "audit_events": audit_events, "final": final}
        print(json.dumps(output, indent=2 if args.pretty else None, ensure_ascii=False))
        return 0

    retrieval = retrieval_payload(request, workflow_state)

    common_payload = {
        "request_text": request_text,
        "evidence_sources": retrieval["evidence_sources"],
        "retrieval_context": {
            "provider": retrieval["provider"],
            "query_terms": retrieval["query_terms"],
            "hits": retrieval["hits"],
        },
        "instructions": request.get("instructions"),
        "assumptions": request.get("assumptions", []),
        "decision_context": request.get("decision_context"),
    }

    steps: list[dict[str, Any]] = []
    primary_role = resolve_primary_role(workflow_state["intent_class"], workflow_state, roles_by_slug, routing_policy)
    review_role = resolve_review_role(primary_role, workflow_state["intent_class"], roles_by_slug, routing_policy)

    if workflow_state.get("decision_gate") == "REVIEW_NEEDED":
        audit_events.append(build_audit_event(trace_id, "governance_gate_triggered", ROLE_YAYAK, trace_id, workflow_state.get("decision_reason")))
    if workflow_state.get("human_touchpoint_required"):
        audit_events.append(build_audit_event(trace_id, "human_touchpoint_required", ROLE_YAYAK, trace_id, workflow_state.get("approval_gate")))

    primary_handoff = build_handoff(trace_id=trace_id, from_role=ROLE_YAYAK, to_role=primary_role, sequence=1, task_summary=task_summary_for(primary_role, roles_by_slug, "primary"), workflow_state={**workflow_state, "current_owner_role": ROLE_YAYAK, "next_owner_role": primary_role}, payload=common_payload)
    audit_events.append(build_audit_event(trace_id, "handoff_created", ROLE_YAYAK, primary_handoff["handoff_id"], primary_handoff["task_summary"]))
    primary_response = runner.run(primary_handoff)
    audit_events.extend(emit_response_audit_events(trace_id, primary_handoff, primary_response))
    steps.append({"handoff": primary_handoff, "response": primary_response})

    if review_role:
        review_payload = {**common_payload, "draft_artifact": primary_response.get("artifact")}
        review_handoff = build_handoff(trace_id=trace_id, from_role=primary_role, to_role=review_role, sequence=2, task_summary=task_summary_for(review_role, roles_by_slug, "review"), workflow_state={**workflow_state, "current_owner_role": primary_role, "next_owner_role": review_role}, payload=review_payload)
        audit_events.append(build_audit_event(trace_id, "handoff_created", primary_role, review_handoff["handoff_id"], review_handoff["task_summary"]))
        review_response = runner.run(review_handoff)
        audit_events.extend(emit_response_audit_events(trace_id, review_handoff, review_response))
        steps.append({"handoff": review_handoff, "response": review_response})

    final = build_terminal_state(trace_id, workflow_state, steps, roles_by_slug, retrieval)
    audit_events.append(build_audit_event(trace_id, "workflow_terminalized", ROLE_YAYAK, "final", final["status"]))

    output = {
        "contract_version": CONTRACT_VERSION,
        "trace_id": trace_id,
        "workflow_state": workflow_state,
        "steps": steps,
        "audit_events": audit_events,
        "final": final,
    }
    print(json.dumps(output, indent=2 if args.pretty else None, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
