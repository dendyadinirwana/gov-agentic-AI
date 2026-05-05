#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORCHESTRATOR = ROOT / "scripts" / "agent_to_agent_orchestrator.py"
EXAMPLE = ROOT / "examples" / "agent-to-agent" / "yayak-alfian-edi.request.json"


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(ORCHESTRATOR), "--input-json", str(EXAMPLE)],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)

    assert payload["workflow_state"]["current_owner_role"] == "top-layer__gov-ai_yayak"
    assert len(payload["steps"]) == 2
    assert payload["steps"][0]["handoff"]["to_role"] == "komunikasi-dan-dokumen__penulis-naskah_alfian"
    assert payload["steps"][1]["handoff"]["to_role"] == "kebijakan-dan-hukum__monitor-kepatuhan-hukum_edi"
    assert payload["steps"][0]["response"]["artifact"]
    assert payload["final"]["trace_id"] == payload["trace_id"]

    print("PASS: agent-to-agent first slice smoke test")
    print(json.dumps({
        "trace_id": payload["trace_id"],
        "final_status": payload["final"]["final_status"],
        "red_flags": payload["final"]["red_flags"],
        "recommended_next_step": payload["final"]["recommended_next_step"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
