#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_VERSION = "a2a.v1"
DECISIONS = {"approve", "reject", "hold", "escalate"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_review_packet(workflow: dict[str, Any]) -> dict[str, Any]:
    final = workflow.get("final", {})
    review_required = final.get("final_status") in {"needs_review", "blocked", "failed"} or bool((final.get("workflow_state") or {}).get("human_touchpoint_required"))
    return {
        "contract_version": CONTRACT_VERSION,
        "review_id": f"review-{uuid.uuid4().hex[:12]}",
        "trace_id": workflow["trace_id"],
        "packet_created_at": datetime.now(timezone.utc).isoformat(),
        "review_required": review_required,
        "packet_summary": final.get("summary"),
        "final_status": final.get("final_status"),
        "recommended_next_step": final.get("recommended_next_step"),
        "red_flags": final.get("red_flags", []),
        "execution_path": final.get("execution_path", []),
        "retrieval": final.get("retrieval", {}),
        "workflow_state": final.get("workflow_state", {}),
        "audit_events": workflow.get("audit_events", []),
        "source_workflow_ref": workflow.get("trace_id"),
    }


def build_review_decision(packet: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    if args.decision not in DECISIONS:
        raise ValueError(f"unsupported decision: {args.decision}")
    return {
        "contract_version": CONTRACT_VERSION,
        "trace_id": packet["trace_id"],
        "review_id": packet["review_id"],
        "packet_ref": packet["source_workflow_ref"],
        "decision": args.decision,
        "reviewer": {
            "actor_id": args.actor_id,
            "actor_role": args.actor_role,
            "display_name": args.display_name or args.actor_id,
        },
        "notes": args.notes or "",
        "decided_at": datetime.now(timezone.utc).isoformat(),
        "resume_allowed": args.decision == "approve",
        "escalation_target": args.escalation_target if args.decision == "escalate" else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal HITL review console for Gov-Agentic AI")
    sub = parser.add_subparsers(dest="command", required=True)

    packet = sub.add_parser("packet", help="Create review packet from workflow output")
    packet.add_argument("--workflow-json", required=True)
    packet.add_argument("--output-json", required=True)

    decide = sub.add_parser("decide", help="Create review decision from review packet")
    decide.add_argument("--packet-json", required=True)
    decide.add_argument("--decision", required=True, choices=sorted(DECISIONS))
    decide.add_argument("--actor-id", required=True)
    decide.add_argument("--actor-role", required=True)
    decide.add_argument("--display-name")
    decide.add_argument("--notes", default="")
    decide.add_argument("--escalation-target")
    decide.add_argument("--output-json", required=True)

    args = parser.parse_args()

    if args.command == "packet":
        workflow = load_json(Path(args.workflow_json))
        review_packet = build_review_packet(workflow)
        save_json(Path(args.output_json), review_packet)
        print(json.dumps(review_packet, ensure_ascii=False, indent=2))
        return 0

    if args.command == "decide":
        packet_data = load_json(Path(args.packet_json))
        decision = build_review_decision(packet_data, args)
        save_json(Path(args.output_json), decision)
        print(json.dumps(decision, ensure_ascii=False, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
