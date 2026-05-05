#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORCHESTRATOR = ROOT / "scripts" / "agent_to_agent_orchestrator.py"
EXAMPLES = ROOT / "examples" / "agent-to-agent"

CASES = [
    {
        "file": "yayak-alfian-edi.request.json",
        "expected_steps": 2,
        "expected_path": ["Alfian", "Edi"],
        "expected_status": "needs_review",
    },
    {
        "file": "budget-review.request.json",
        "expected_steps": 1,
        "expected_path": ["Anastasia"],
        "expected_status": "completed",
    },
    {
        "file": "procurement-neutrality.request.json",
        "expected_steps": 1,
        "expected_path": ["Hafidus"],
        "expected_status": "completed",
    },
    {
        "file": "archive-record.request.json",
        "expected_steps": 2,
        "expected_path": ["Sovia", "Izza"],
        "expected_status": "completed",
    },
    {
        "file": "escalation-blocker.request.json",
        "expected_steps": 1,
        "expected_path": ["Winda"],
        "expected_status": "needs_review",
    },
    {
        "file": "retrieval-budget-review.request.json",
        "expected_steps": 1,
        "expected_path": ["Anastasia"],
        "expected_status": "completed",
    },
    {
        "file": "hitl-review.request.json",
        "expected_steps": 2,
        "expected_path": ["Alfian", "Edi"],
        "expected_status": "needs_review",
    },
]


def main() -> int:
    results = []
    for case in CASES:
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), "--input-json", str(EXAMPLES / case["file"])],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        assert len(payload["steps"]) == case["expected_steps"], case["file"]
        assert payload["final"]["execution_path"] == case["expected_path"], case["file"]
        assert payload["final"]["final_status"] == case["expected_status"], case["file"]
        results.append({
            "file": case["file"],
            "final_status": payload["final"]["final_status"],
            "execution_path": payload["final"]["execution_path"],
        })

    print("PASS: agent-to-agent fixture matrix smoke test")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
