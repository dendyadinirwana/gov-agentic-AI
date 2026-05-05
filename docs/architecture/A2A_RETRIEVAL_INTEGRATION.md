# A2A Retrieval Integration

Dokumen ini menjelaskan retrieval contract awal untuk Gov-Agentic AI MVP.

## Tujuan
Menambahkan grounding berbasis dokumen tanpa harus membangun RAG stack penuh lebih dulu.

## Bentuk Integrasi MVP
Retrieval memakai provider lokal deterministik:
- config: `configs/retrieval.generated.json`
- retriever: `scripts/local_retriever.py`
- corpus contoh: `examples/retrieval-corpus/government_sources.json`

## Request Contract
Request orchestrator boleh menambahkan:
- `retrieval_required: true|false`
- `evidence_sources: []` sebagai seed manual awal bila ada

Jika `retrieval_required=true`, orchestrator akan:
1. resolve query terms dari `request_text` + `intent_class`
2. ambil hit dari local corpus
3. inject hasil ke `handoff.payload.retrieval_context`
4. merge title hit ke `handoff.payload.evidence_sources`

## Handoff Payload Additions
Field baru pada payload:
- `retrieval_context.provider`
- `retrieval_context.query_terms`
- `retrieval_context.hits[]`

Setiap hit minimal membawa provenance:
- `source_id`
- `title`
- `owner`
- `document_type`
- `classification`
- `issue_date`
- `uri`
- `excerpt`

## Response Provenance
`role_runtime_adapter.py` sekarang memetakan retrieval hit ke `response.evidence_map` dengan:
- `use: retrieved evidence`
- provenance fields tetap utuh

Source manual non-retrieval tetap masuk sebagai:
- `use: working evidence`

## Terminal Output
`final.retrieval` sekarang menyimpan:
- `required`
- `provider`
- `query_terms`
- `hit_count`
- `sources[]` ringkas untuk audit/provenance trail

## Runnable Example
Gunakan:
- `examples/agent-to-agent/retrieval-budget-review.request.json`

Test/validation:
- `python3 -m unittest discover -s tests -v`
- `python3 scripts/smoke_test_agent_to_agent_matrix.py`
- `python3 scripts/agent_to_agent_orchestrator.py --input-json examples/agent-to-agent/retrieval-budget-review.request.json --pretty`

## Batasan MVP
- belum ada vector search
- ranking masih keyword-score deterministic
- corpus masih file JSON lokal
- belum ada freshness/authority weighting lanjutan

## Next Evolution
Setelah MVP retrieval ini stabil, langkah lanjut paling natural:
1. authority weighting per source type
2. update/freshness scoring
3. role-specific retrieval filters
4. real retrieval backend / indexed corpus
5. citation binding dari claim ke source chunk
