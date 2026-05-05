# A2A HITL Review Console

Dokumen ini menjelaskan jalur human-in-the-loop (HITL) minimum yang runnable untuk Gov-Agentic AI.

## Tujuan
Mengubah governance gate dari konsep menjadi alur operasional yang bisa:
- membuat review packet
- menerima keputusan manusia
- memfinalkan status workflow
- mencatat audit event manusia

## Kontrak Inti
### 1. Review packet
Dihasilkan dari output orchestrator yang butuh review.
Field penting:
- `review_id`
- `trace_id`
- `review_required`
- `packet_summary`
- `final_status`
- `recommended_next_step`
- `red_flags`
- `execution_path`
- `workflow_state`
- `source_workflow_ref`

### 2. Review decision
Schema:
- `schemas/hitl_review_decision.schema.json`

Keputusan yang didukung:
- `approve`
- `reject`
- `hold`
- `escalate`

### 3. Resume/finalize
Decision manusia dipakai untuk menghasilkan terminal state final yang baru:
- approve → `completed`
- reject → `failed`
- hold → `blocked`
- escalate → `needs_review`

## CLI Minimal
Script:
- `scripts/hitl_review_console.py`

### Buat packet
```bash
python3 scripts/hitl_review_console.py packet \
  --workflow-json /tmp/workflow.json \
  --output-json /tmp/review-packet.json
```

### Buat decision
```bash
python3 scripts/hitl_review_console.py decide \
  --packet-json /tmp/review-packet.json \
  --decision approve \
  --actor-id reviewer-1 \
  --actor-role human-reviewer \
  --display-name "Reviewer Internal" \
  --notes "Dapat dilanjutkan" \
  --output-json /tmp/review-decision.json
```

### Resume workflow
```bash
python3 scripts/agent_to_agent_orchestrator.py \
  --input-json examples/agent-to-agent/hitl-review.request.json \
  --review-decision-json /tmp/review-decision.json \
  --pretty
```

## Audit Semantics
Aksi manusia memunculkan event baru:
- `human_review_decision`
- `workflow_resumed`

## Batasan MVP
- belum ada UI web
- packet storage masih file JSON
- resume masih finalization-oriented, belum re-run branch kompleks
- reviewer identity masih caller-supplied, belum IAM-backed
