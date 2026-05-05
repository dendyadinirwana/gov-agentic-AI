#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from a2a_contracts import validate_handoff, validate_response

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CONFIGS = ROOT / "configs"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


class RoleRunner:
    def run(self, handoff: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class LocalAdapterRunner(RoleRunner):
    def __init__(self, adapter_mode: str = "local-mock", runtime_config_path: Path | None = None) -> None:
        self.adapter_mode = adapter_mode
        self.runtime_config_path = runtime_config_path or (CONFIGS / "runtime.generated.json")

    def run(self, handoff: dict[str, Any]) -> dict[str, Any]:
        errors = validate_handoff(handoff)
        if errors:
            raise ValueError("invalid handoff: " + "; ".join(errors))
        adapter = SCRIPTS / "role_runtime_adapter.py"
        temp = ROOT / ".tmp_a2a_handoff.json"
        temp.write_text(json.dumps(handoff, ensure_ascii=False, indent=2), encoding="utf-8")
        try:
            cmd = [
                sys.executable,
                str(adapter),
                "--input-json",
                str(temp),
                "--adapter-mode",
                self.adapter_mode,
                "--runtime-config",
                str(self.runtime_config_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            response = json.loads(result.stdout)
        finally:
            if temp.exists():
                temp.unlink()
        errors = validate_response(response, handoff)
        if errors:
            raise ValueError("invalid response: " + "; ".join(errors))
        return response


def build_role_runner(runtime_target: str = "generic", runtime_config_path: Path | None = None) -> RoleRunner:
    runtime_config = {}
    if runtime_config_path and runtime_config_path.exists():
        runtime_config = load_json(runtime_config_path)
    adapter_exec = runtime_config.get("a2a_adapter_execution", {}) if isinstance(runtime_config, dict) else {}
    prefer_real = bool(adapter_exec.get("prefer_real_runtime", False))
    mode_map = {
        "generic": "local-mock",
        "hermes": "hermes-real" if prefer_real else "hermes-mock",
        "openclaw": "openclaw-real" if prefer_real else "openclaw-mock",
    }
    return LocalAdapterRunner(mode_map.get(runtime_target, "local-mock"), runtime_config_path=runtime_config_path)
