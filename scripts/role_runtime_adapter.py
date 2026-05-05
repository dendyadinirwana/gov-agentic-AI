#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shlex
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from string import Template
from typing import Any

from a2a_contracts import validate_handoff, validate_response

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / "configs"
CONTRACT_VERSION = "a2a.v1"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_role_registry() -> dict[str, Any]:
    return load_json(CONFIGS / "role_registry.json")


def load_runtime_config(path: Path | None) -> dict[str, Any]:
    target = path or (CONFIGS / "runtime.generated.json")
    if target.exists():
        return load_json(target)
    return {}


def index_roles(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {role["role_slug"]: role for role in registry["roles"]}


def _build_evidence_map(evidence_sources: list[str], retrieval_hits: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    hits = retrieval_hits or []
    mapped = []
    matched_titles = set()
    for hit in hits:
        title = hit.get("title")
        if title:
            matched_titles.add(title)
        mapped.append({
            "source": title or hit.get("source_id") or "retrieved source",
            "use": "retrieved evidence",
            "source_id": hit.get("source_id"),
            "owner": hit.get("owner"),
            "document_type": hit.get("document_type"),
            "classification": hit.get("classification"),
            "issue_date": hit.get("issue_date"),
            "uri": hit.get("uri"),
            "excerpt": hit.get("excerpt"),
        })
    for source in evidence_sources:
        if source in matched_titles:
            continue
        mapped.append({"source": source, "use": "working evidence"})
    return mapped


def _mk_response(
    trace_id: str,
    role_slug: str,
    status: str,
    summary: str,
    artifact: str | None,
    evidence_sources: list[str],
    assumptions: list[str],
    confidence: str,
    red_flags: list[str],
    human_required: bool,
    human_reason: str,
    next_step: str,
    adapter_mode: str,
    runtime_behavior: str = "mocked-local-role-execution",
    runtime_details: dict[str, Any] | None = None,
    audit_hints: dict[str, Any] | None = None,
    retrieval_hits: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    response = {
        "contract_version": CONTRACT_VERSION,
        "trace_id": trace_id,
        "response_id": f"resp-{uuid.uuid4().hex[:12]}",
        "role_slug": role_slug,
        "status": status,
        "summary": summary,
        "artifact": artifact,
        "evidence_map": _build_evidence_map(evidence_sources, retrieval_hits),
        "assumptions": assumptions,
        "confidence": confidence,
        "red_flags": red_flags,
        "human_touchpoint": {
            "required": human_required,
            "reason": human_reason,
        },
        "next_step": next_step,
        "adapter_execution": {
            "mode": adapter_mode,
            "runtime_behavior": runtime_behavior,
            "details": runtime_details or {},
            "audit_hints": audit_hints or {},
            "runtime_contract": (runtime_details or {}).get("runtime_contract", {}),
        },
        "audit": {
            "handled_at": datetime.now(timezone.utc).isoformat(),
            "handled_by": role_slug,
            "adapter_mode": adapter_mode,
        },
    }
    return response


def generic_artifact_for(role: dict[str, Any], request_text: str, prior_artifact: str | None) -> str | None:
    role_name = role.get("role", role.get("role_slug", "Role"))
    role_class = (role.get("authority") or {}).get("role_class", "specialist")
    if prior_artifact:
        return prior_artifact
    if role_class == "specialist" and role_name in {"Penulis Naskah", "Notulis", "Penerjemah Kebijakan", "Admin Persuratan", "Asisten Disposisi"}:
        return f"DRAFT OUTPUT - {role_name}\n\nRingkasan tugas: {request_text}\n\nCatatan: Artefak ini masih memerlukan review sesuai governance."
    return None


def generic_response(handoff: dict[str, Any], role: dict[str, Any], adapter_mode: str) -> dict[str, Any]:
    role_slug = handoff["to_role"]
    trace_id = handoff["trace_id"]
    request_text = handoff["payload"]["request_text"]
    evidence_sources = handoff["payload"].get("evidence_sources", [])
    draft_artifact = handoff["payload"].get("draft_artifact")
    governance = handoff["governance"]
    retrieval_hits = ((handoff["payload"].get("retrieval_context") or {}).get("hits") or [])
    role_name = role.get("role", role_slug)
    role_class = (role.get("authority") or {}).get("role_class", "specialist")
    use_cases = (role.get("orchestration") or {}).get("primary_use_cases", [])
    focus = use_cases[0] if use_cases else "role-specific work"
    artifact = generic_artifact_for(role, request_text, draft_artifact)

    red_flags = []
    if not evidence_sources:
        red_flags.append("Evidence source belum dilampirkan.")
    if not retrieval_hits and handoff["payload"].get("retrieval_context", {}).get("provider") not in {None, "disabled"}:
        red_flags.append("Retrieval context diharapkan tetapi tidak menghasilkan source provenance.")
    if governance.get("human_touchpoint_required"):
        red_flags.append("Output ini tetap memerlukan review atau keputusan manusia sebelum dipakai resmi.")

    status = "needs_review" if red_flags else "completed"
    summary = f"{role_name} menjalankan tugas {focus} berdasarkan handoff dari orchestrator."
    next_step = "Kembalikan hasil ke orchestrator untuk diringkas, diteruskan, atau dieskalasikan sesuai governance."
    assumptions = [
        f"Peran dijalankan sebagai {role_class} berbasis metadata registry.",
        f"Adapter berjalan dalam mode {adapter_mode}; bila runtime nyata belum siap maka fallback ke mock digunakan."
    ]

    return _mk_response(trace_id, role_slug, status, summary, artifact, evidence_sources, assumptions, "medium", red_flags, governance.get("human_touchpoint_required", False), "Mengikuti governance gate dan status runtime adapter.", next_step, adapter_mode, retrieval_hits=retrieval_hits)


def _runtime_settings(runtime_config: dict[str, Any], adapter_mode: str) -> dict[str, Any]:
    cfg = runtime_config.get("a2a_adapter_execution", {}) if isinstance(runtime_config, dict) else {}
    modes = cfg.get("modes", {}) if isinstance(cfg, dict) else {}
    return modes.get(adapter_mode, {}) if isinstance(modes, dict) else {}


def _render_command(template_or_command: str, *, handoff_path: str, role_slug: str, trace_id: str) -> str:
    rendered = Template(template_or_command).safe_substitute(
        handoff_path=handoff_path,
        role_slug=role_slug,
        trace_id=trace_id,
    )
    return rendered


def _runtime_contract(adapter_mode: str, settings: dict[str, Any], resolved_command: str | None, command_source: str) -> dict[str, Any]:
    return {
        "adapter_mode": adapter_mode,
        "command_source": command_source,
        "env_command_var": settings.get("env_command_var"),
        "supports_placeholders": ["$handoff_path", "$role_slug", "$trace_id"],
        "resolved_command": resolved_command,
        "stdout_contract": settings.get("stdout_contract", "a2a-response-json|json-object|plain-text"),
        "timeout_seconds": int(settings.get("timeout_seconds", 120)),
    }


def _normalize_real_runtime_output(raw: str, handoff: dict[str, Any], adapter_mode: str, role_slug: str) -> dict[str, Any]:
    text = raw.strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict) and parsed.get("contract_version") == CONTRACT_VERSION:
            return parsed
        if isinstance(parsed, dict):
            return _mk_response(
                handoff["trace_id"],
                role_slug,
                parsed.get("status", "completed"),
                parsed.get("summary", f"Runtime {adapter_mode} menyelesaikan peran {role_slug}."),
                parsed.get("artifact"),
                handoff["payload"].get("evidence_sources", []),
                parsed.get("assumptions", [f"Output dinormalisasi dari runtime {adapter_mode}."]),
                parsed.get("confidence", "medium"),
                parsed.get("red_flags", []),
                parsed.get("human_touchpoint", {}).get("required", handoff["governance"].get("human_touchpoint_required", False)),
                parsed.get("human_touchpoint", {}).get("reason", "Mengikuti hasil runtime nyata."),
                parsed.get("next_step", "Kembalikan hasil ke orchestrator."),
                adapter_mode,
                runtime_behavior="real-runtime-command",
                runtime_details={"normalized_from": "json-object"},
            )
    except Exception:
        pass
    return _mk_response(
        handoff["trace_id"],
        role_slug,
        "completed",
        text or f"Runtime {adapter_mode} selesai tanpa ringkasan eksplisit.",
        None,
        handoff["payload"].get("evidence_sources", []),
        [f"Output teks biasa dari runtime {adapter_mode} dinormalisasi ke kontrak A2A."],
        "medium",
        [],
        handoff["governance"].get("human_touchpoint_required", False),
        "Runtime nyata tidak mengembalikan kontrak penuh; hasil dinormalisasi oleh adapter.",
        "Kembalikan hasil ke orchestrator untuk validasi lanjutan.",
        adapter_mode,
        runtime_behavior="real-runtime-command",
        runtime_details={"normalized_from": "plain-text"},
    )


def try_real_runtime(handoff: dict[str, Any], runtime_config: dict[str, Any], adapter_mode: str) -> dict[str, Any] | None:
    settings = _runtime_settings(runtime_config, adapter_mode)
    env_command_var = settings.get("env_command_var", "")
    command = settings.get("command") or os.environ.get(env_command_var, "")
    if not command:
        return None
    timeout = int(settings.get("timeout_seconds", 120))
    role_slug = handoff["to_role"]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        fh.write(json.dumps(handoff, ensure_ascii=False, indent=2))
        handoff_path = fh.name
    command_source = "config.command" if settings.get("command") else f"env:{env_command_var}"
    resolved_command = _render_command(command, handoff_path=handoff_path, role_slug=role_slug, trace_id=handoff["trace_id"])
    runtime_contract = _runtime_contract(adapter_mode, settings, resolved_command, command_source)
    try:
        env = os.environ.copy()
        env["GOV_AGENTIC_A2A_HANDOFF_PATH"] = handoff_path
        env["GOV_AGENTIC_A2A_ROLE_SLUG"] = role_slug
        env["GOV_AGENTIC_A2A_TRACE_ID"] = handoff["trace_id"]
        cmd = shlex.split(resolved_command)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env, cwd=str(ROOT))
        if result.returncode != 0:
            return _mk_response(
                handoff["trace_id"],
                role_slug,
                "needs_review",
                f"Runtime {adapter_mode} gagal dieksekusi; adapter fallback mengembalikan hasil untuk review manusia.",
                None,
                handoff["payload"].get("evidence_sources", []),
                [f"Command runtime nyata gagal dengan code {result.returncode}; fallback digunakan."],
                "low",
                [result.stderr.strip() or "runtime command returned non-zero exit"],
                True,
                "Eksekusi runtime nyata gagal; perlu verifikasi operator sebelum melanjutkan.",
                "Periksa konfigurasi command runtime lalu ulangi handoff.",
                adapter_mode,
                runtime_behavior="real-runtime-command-failed",
                runtime_details={"returncode": result.returncode, "stderr": result.stderr.strip(), "runtime_contract": runtime_contract},
                audit_hints={"runtime_failed": True, "fallback_used": False, "human_touchpoint_required": True},
            )
        normalized = _normalize_real_runtime_output(result.stdout, handoff, adapter_mode, role_slug)
        normalized.setdefault("adapter_execution", {}).setdefault("details", {}).update({"runtime_contract": runtime_contract})
        normalized.setdefault("adapter_execution", {})["runtime_contract"] = runtime_contract
        return normalized
    except subprocess.TimeoutExpired:
        return _mk_response(
            handoff["trace_id"],
            role_slug,
            "needs_review",
            f"Runtime {adapter_mode} timeout; adapter mengembalikan status review-needed.",
            None,
            handoff["payload"].get("evidence_sources", []),
            ["Eksekusi runtime nyata melebihi batas waktu adapter."],
            "low",
            ["runtime command timeout"],
            True,
            "Runtime nyata timeout; perlu intervensi operator.",
            "Periksa runtime command atau naikkan timeout lalu ulangi.",
            adapter_mode,
            runtime_behavior="real-runtime-command-timeout",
            runtime_details={"timeout_seconds": timeout, "runtime_contract": runtime_contract},
            audit_hints={"runtime_timeout": True, "fallback_used": False, "human_touchpoint_required": True},
        )
    finally:
        try:
            Path(handoff_path).unlink(missing_ok=True)
        except Exception:
            pass


def execute_role(handoff: dict[str, Any], adapter_mode: str = "local-mock", runtime_config_path: Path | None = None) -> dict[str, Any]:
    errors = validate_handoff(handoff)
    if errors:
        raise ValueError("invalid handoff: " + "; ".join(errors))

    registry = load_role_registry()
    roles_by_slug = index_roles(registry)
    runtime_config = load_runtime_config(runtime_config_path)

    role_slug = handoff["to_role"]
    trace_id = handoff["trace_id"]
    request_text = handoff["payload"]["request_text"]
    evidence_sources = handoff["payload"].get("evidence_sources", [])
    draft_artifact = handoff["payload"].get("draft_artifact")
    governance = handoff["governance"]
    role = roles_by_slug.get(role_slug, {"role_slug": role_slug, "role": role_slug})

    fallback_hint = None
    if adapter_mode in {"hermes-real", "openclaw-real"}:
        real_response = try_real_runtime(handoff, runtime_config, adapter_mode)
        if real_response is not None:
            errors = validate_response(real_response, handoff)
            if errors:
                raise ValueError("invalid response: " + "; ".join(errors))
            return real_response
        original_mode = adapter_mode
        adapter_mode = "hermes-mock" if adapter_mode == "hermes-real" else "openclaw-mock"
        fallback_hint = {
            "fallback_used": True,
            "fallback_from": original_mode,
            "fallback_to": adapter_mode,
            "human_touchpoint_required": handoff["governance"].get("human_touchpoint_required", False),
        }

    if role_slug == "komunikasi-dan-dokumen__penulis-naskah_alfian":
        artifact = draft_artifact or (
            "DRAFT NOTA DINAS\n"
            "Perihal: Tindak lanjut permintaan\n\n"
            "Ringkasan: " + request_text + "\n\n"
            "Catatan: Draf ini masih membutuhkan review kepatuhan sebelum diproses lebih lanjut."
        )
        response = _mk_response(
            trace_id, role_slug, "completed", "Alfian menyusun draf formal awal berdasarkan permintaan dan evidence yang tersedia.", artifact,
            evidence_sources,
            ["Format keluaran yang dibutuhkan adalah draf formal internal.", "Evidence yang diberikan cukup untuk menyusun draf awal, belum untuk finalisasi."],
            "medium",
            ["Belum ada validasi kepatuhan hukum pada draf.", "Draf tidak boleh diperlakukan sebagai keputusan final."],
            governance.get("human_touchpoint_required", False),
            "Permintaan berdampak pada artefak formal dan butuh review sebelum digunakan resmi.",
            "Teruskan draf ke Monitor Kepatuhan Hukum (Edi) untuk review kepatuhan.",
            adapter_mode,
            audit_hints=fallback_hint,
        )
    elif role_slug == "kebijakan-dan-hukum__monitor-kepatuhan-hukum_edi":
        red_flags = []
        if "nomor" not in request_text.lower():
            red_flags.append("Basis nomor atau referensi dokumen belum terlihat eksplisit di request.")
        if not evidence_sources:
            red_flags.append("Tidak ada evidence source yang dilampirkan.")
        status = "needs_review" if red_flags else "completed"
        summary = "Edi meninjau draf dan menemukan gap kontrol yang perlu diakui sebelum artefak dipakai resmi." if red_flags else "Edi meninjau draf dan tidak menemukan gap kontrol material pada evidence yang tersedia."
        response = _mk_response(
            trace_id, role_slug, status, summary, draft_artifact, evidence_sources,
            ["Review ini bersifat kontrol kepatuhan awal, bukan persetujuan hukum final."],
            "medium" if red_flags else "high", red_flags, True,
            "Temuan monitor harus diakui oleh owner manusia sebelum artefak dipakai resmi.",
            "Kembalikan ke Yayak untuk diringkas menjadi rekomendasi tindak lanjut + human review gate.",
            adapter_mode,
            audit_hints={**(fallback_hint or {}), "review_returned": bool(red_flags), "human_touchpoint_required": True},
        )
    elif role_slug == "top-layer__gov-ai_yayak":
        response = _mk_response(
            trace_id, role_slug, "completed", "Yayak menerima hasil lintas peran dan menyusunnya menjadi ringkasan orkestrasi.", None,
            evidence_sources, [], "high", [], governance.get("human_touchpoint_required", False),
            "Mengikuti gate governance dari decision engine.", "Sampaikan hasil ke user atau teruskan ke owner manusia yang relevan.", adapter_mode,
            audit_hints=fallback_hint,
        )
    else:
        response = generic_response(handoff, role, adapter_mode)
        if fallback_hint:
            response.setdefault("adapter_execution", {}).setdefault("audit_hints", {}).update(fallback_hint)

    errors = validate_response(response, handoff)
    if errors:
        raise ValueError("invalid response: " + "; ".join(errors))
    return response


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Runtime adapter for Gov-Agentic AI roles.")
    parser.add_argument("--input-json", required=True, help="Path to agent handoff JSON")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--adapter-mode", default="local-mock")
    parser.add_argument("--runtime-config", default=str(CONFIGS / "runtime.generated.json"))
    args = parser.parse_args()

    with open(args.input_json, "r", encoding="utf-8") as fh:
        handoff = json.load(fh)
    response = execute_role(handoff, adapter_mode=args.adapter_mode, runtime_config_path=Path(args.runtime_config))
    print(json.dumps(response, indent=2 if args.pretty else None, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
