# Agent-to-Agent Contracts and Runtime

## Purpose
Dokumen ini menjelaskan kontrak formal, lifecycle orkestrasi, dan mode eksekusi runtime untuk arsitektur agent-to-agent (A2A) pada Gov-Agentic AI.

Tujuannya bukan menjelaskan persona tiap role, tetapi menjelaskan *bagaimana* satu role menyerahkan kerja ke role lain secara konsisten, ter-audit, dan tetap patuh governance.

## Canonical sources
Backbone A2A saat ini memakai sumber kanonik berikut:

- `configs/role_registry.json`
  - metadata role
  - routing policy
  - intent detection
  - review fallback
  - action/sensitivity/impact/work-state policy
- `scripts/government_decision_engine.py`
  - consumer tipis untuk policy di registry
- `scripts/agent_to_agent_orchestrator.py`
  - orchestrator utama
- `scripts/role_runner.py`
  - role execution abstraction
- `scripts/role_runtime_adapter.py`
  - runtime adapter dan contract normalization

## Contract version
Versi kontrak aktif:

- `a2a.v1`

Kontrak ini dipakai di:
- handoff antar role
- response dari role
- audit event
- terminal/final workflow state

## Contract files
Schema formal saat ini:

- `schemas/agent_to_agent_handoff.schema.json`
- `schemas/agent_to_agent_response.schema.json`
- `schemas/agent_to_agent_terminal_state.schema.json`
- `schemas/agent_to_agent_audit_event.schema.json`

Validator Python:

- `scripts/a2a_contracts.py`

## Lifecycle orchestration
Lifecycle standar A2A saat ini:

1. **Request intake**
   - request diterima orchestrator
   - owner awal default: `top-layer__gov-ai_yayak`
2. **Decision build**
   - decision engine menghitung:
     - `intent_class`
     - `action_level`
     - `work_state`
     - `decision_gate`
     - `human_touchpoint_required`
3. **Primary handoff**
   - orchestrator membuat `handoff`
   - payload dikirim ke role utama
4. **Role execution**
   - role runner mengeksekusi adapter
   - adapter mengembalikan `response`
5. **Review handoff** *(jika perlu)*
   - orchestrator meneruskan artefak ke role review
6. **Terminalization**
   - orchestrator menyusun `final`
   - audit events ditutup

## Contract surfaces

### 1) Handoff
Handoff adalah unit kerja formal yang dikirim dari satu role ke role lain.

Field penting:
- `contract_version`
- `trace_id`
- `handoff_id`
- `from_role`
- `to_role`
- `intent_class`
- `task_summary`
- `action_level`
- `workflow_state`
- `payload`
- `governance`
- `audit`

### 2) Response
Response adalah hasil terstruktur dari role target.

Field penting:
- `contract_version`
- `trace_id`
- `response_id`
- `role_slug`
- `status`
- `summary`
- `artifact`
- `evidence_map`
- `assumptions`
- `confidence`
- `red_flags`
- `human_touchpoint`
- `next_step`
- `adapter_execution`
- `audit`

### 3) Audit event
Audit event mencatat event lifecycle penting.

Event type saat ini:
- `handoff_created` → `info` / `operational_record` / `standard` / `log_only`
- `role_response_recorded` → `info` / `operational_record` / `standard` / `log_only`
- `workflow_terminalized` → `info` / `governance_record` / `standard` / `log_only`
- `governance_gate_triggered` → `warning` / `governance_record` / `governance_control` / `review_required`
- `human_touchpoint_required` → `warning` / `governance_record` / `human_approval` / `ack_required`
- `fallback_used` → `warning` / `governance_record` / `governance_control` / `review_required`
- `review_returned` → `warning` / `governance_record` / `human_approval` / `review_required`
- `runtime_failed` → `critical` / `incident_record` / `runtime_incident` / `escalate_required`
- `runtime_timeout` → `critical` / `incident_record` / `runtime_incident` / `escalate_required`
- `human_review_decision` → `warning` / `governance_record` / `human_approval` / `ack_required`
- `workflow_resumed` → `info` / `governance_record` / `human_approval` / `log_only`

### 4) Terminal state
Terminal state adalah ringkasan final workflow.

Field penting:
- `status`
- `final_status` *(alias kompatibilitas untuk flow lama)*
- `summary`
- `workflow_state`
- `recommended_next_step`
- `red_flags`
- `final_artifact`
- `execution_path`

## Runtime execution modes
Role execution saat ini mendukung dua keluarga mode:

### Mock modes
- `local-mock`
- `hermes-mock`
- `openclaw-mock`

Dipakai untuk:
- smoke test
- local validation
- fallback aman saat runtime nyata belum siap

Karakteristik:
- deterministic
- contract-stable
- tidak invoke agent runtime eksternal

### Real modes
- `hermes-real`
- `openclaw-real`

Dipakai melalui `role_runtime_adapter.py` dan diaktifkan oleh:
- `configs/runtime.generated.json`
- `a2a_adapter_execution.prefer_real_runtime`
- command runtime yang didefinisikan lewat env var atau config

Untuk kontrak invocation yang lebih detail — termasuk placeholder command, stdout normalization, dan timeout/failure semantics — lihat `docs/architecture/A2A_RUNTIME_HARDENING.md`.

## Runtime command wiring
Konfigurasi runtime adapter saat ini berada di:
- `configs/runtime.generated.json`
- key: `a2a_adapter_execution`

Struktur minimal:

```json
{
  "a2a_adapter_execution": {
    "prefer_real_runtime": false,
    "modes": {
      "hermes-real": {
        "env_command_var": "GOV_AGENTIC_HERMES_ROLE_CMD",
        "timeout_seconds": 120
      },
      "openclaw-real": {
        "env_command_var": "GOV_AGENTIC_OPENCLAW_ROLE_CMD",
        "timeout_seconds": 120
      }
    }
  }
}
```

Env var yang dipakai:
- `GOV_AGENTIC_HERMES_ROLE_CMD`
- `GOV_AGENTIC_OPENCLAW_ROLE_CMD`

Saat runtime command dijalankan, adapter juga menyuntikkan env berikut:
- `GOV_AGENTIC_A2A_HANDOFF_PATH`
- `GOV_AGENTIC_A2A_ROLE_SLUG`
- `GOV_AGENTIC_A2A_TRACE_ID`

Artinya runtime eksternal bisa membaca handoff dari file JSON dan mengembalikan hasil lewat stdout.

## Real runtime normalization rules
Jika runtime nyata mengembalikan:

### A. Kontrak A2A penuh
Kalau stdout sudah berupa object dengan `contract_version = a2a.v1`, adapter akan pakai langsung.

### B. JSON non-kontrak
Kalau stdout berupa JSON biasa, adapter akan normalisasi ke contract response.

### C. Plain text
Kalau stdout berupa teks biasa, adapter akan bungkus ke response A2A dengan metadata normalization.

## Fallback behavior
Kalau runtime nyata:
- belum punya command
- command gagal
- timeout

maka adapter akan:
- **tidak crash diam-diam**
- mengembalikan response terstruktur
- menandai hasil sebagai `needs_review` bila perlu
- menyimpan alasan pada:
  - `adapter_execution.runtime_behavior`
  - `adapter_execution.details`
  - `red_flags`
  - `assumptions`

Kalau mode real dipilih tapi command tidak tersedia, adapter akan turun ke mode mock yang sesuai:
- `hermes-real` → `hermes-mock`
- `openclaw-real` → `openclaw-mock`

## Governance implication
Fallback ke mock **bukan** berarti pekerjaan resmi selesai.

Implikasinya:
- hasil tetap hanya draft/working output
- audit tetap tercatat
- human review tetap wajib bila governance gate mengharuskan
- operator harus membedakan antara:
  - output hasil runtime nyata
  - output fallback/mock

Perbedaan ini bisa dilihat di `adapter_execution.runtime_behavior`.

## Testing
Test suite saat ini ada di:
- `tests/test_a2a_contracts.py`
- `tests/test_decision_engine_policy.py`

Jalankan:

```bash
python3 -m unittest discover -s tests -v
```

Coverage saat ini mencakup:
- orchestrator output contract shape
- response/handoff/audit/terminal validation
- real-adapter fallback behavior
- declarative policy presence dan default decision behavior

## Current baseline flow
Smoke baseline yang dipertahankan selama refactor:
- Yayak → Alfian → Edi

Ekspektasi saat ini:
- draft formal dibuat oleh Alfian
- review kepatuhan awal dilakukan oleh Edi
- final state: `needs_review`

## What is still intentionally simple
Hal berikut masih sengaja sederhana:
- real adapter belum melakukan deep native integration per runtime
- Hermes/OpenClaw command invocation masih shell-based, bukan SDK-native
- task summary templates masih code-level
- audit event taxonomy sekarang punya severity, retention class, compliance class, dan response policy awal, tetapi belum dipetakan ke SLA operasional atau backend retention enforcement

## Recommended next evolution
Tahap selanjutnya yang paling masuk akal:

1. buat **native role invocation contract** per runtime
   - Hermes native
   - OpenClaw native
2. tambah **golden fixtures** untuk berbagai jalur workflow
3. perluas audit taxonomy
   - `fallback_used`
   - `runtime_failed`
   - `human_gate_triggered`
4. tambahkan policy-driven task summary templates

## Safety rule
Jangan menganggap hasil adapter mock sebagai keputusan final atau keputusan resmi organisasi.
Semua action berlevel consequential tetap mengikuti governance gate, approval owner, dan human-in-the-loop sesuai runtime config dan decision engine.
