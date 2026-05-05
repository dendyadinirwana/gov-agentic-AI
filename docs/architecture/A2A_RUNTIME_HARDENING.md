# A2A Runtime Hardening

Dokumen ini menjelaskan kontrak invocation untuk mode `hermes-real` dan `openclaw-real` pada Gov-Agentic AI MVP.

## Tujuan
Mode real runtime tetap memakai command bridge, tetapi sekarang kontraknya lebih eksplisit, deterministic, dan testable.

## Invocation contract
Setiap runtime real membaca handoff A2A dari command yang dikonfigurasi pada `configs/runtime.generated.json` atau environment variable runtime.

### Supported modes
- `hermes-real`
- `openclaw-real`

### Supported command sources
1. `config.command`
2. `env:<ENV_VAR>`

### Supported placeholders
Command boleh memakai placeholder berikut:
- `$handoff_path`
- `$role_slug`
- `$trace_id`

Contoh:
```bash
python3 scripts/runtime_wrapper_example.py --runtime hermes --handoff $handoff_path --role $role_slug --trace $trace_id
```

## Runtime environment
Adapter juga selalu menyiapkan environment variable berikut:
- `GOV_AGENTIC_A2A_HANDOFF_PATH`
- `GOV_AGENTIC_A2A_ROLE_SLUG`
- `GOV_AGENTIC_A2A_TRACE_ID`

Jadi runtime wrapper bisa pilih antara:
- membaca placeholder CLI args
- membaca environment variables
- atau menggabungkan keduanya

## Expected stdout contract
Stdout runtime boleh berbentuk salah satu dari tiga bentuk ini:

1. **Full A2A response JSON**
   - jika `contract_version == a2a.v1`, adapter menerima apa adanya

2. **Plain JSON object**
   - adapter menormalisasi ke kontrak A2A penuh
   - `adapter_execution.details.normalized_from = json-object`

3. **Plain text**
   - adapter menormalisasi ke kontrak A2A penuh
   - `adapter_execution.details.normalized_from = plain-text`

## Failure semantics
### Non-zero exit
- response menjadi `needs_review`
- `runtime_behavior = real-runtime-command-failed`
- audit hint: `runtime_failed = true`

### Timeout
- response menjadi `needs_review`
- `runtime_behavior = real-runtime-command-timeout`
- audit hint: `runtime_timeout = true`

### Missing command
- adapter tidak crash
- flow turun ke fallback mock mode (`hermes-mock` / `openclaw-mock`)
- audit hint: `fallback_used = true`

## Response metadata
Setiap jalur runtime real sekarang membawa `adapter_execution.runtime_contract`, berisi:
- `adapter_mode`
- `command_source`
- `env_command_var`
- `supports_placeholders`
- `resolved_command`
- `stdout_contract`
- `timeout_seconds`

Ini penting untuk auditability operator dan debugging deployment.

## Example wrapper
Repo menyediakan:
- `scripts/runtime_wrapper_example.py`

Script itu bukan integrasi produksi, tapi referensi minimum untuk:
- bentuk command
- cara baca handoff
- bentuk output JSON object yang akan dinormalisasi adapter

## Recommended next hardening
Tahap berikutnya setelah MVP ini:
1. wrapper runtime spesifik Hermes
2. wrapper runtime spesifik OpenClaw
3. retry / backoff policy untuk transient failure
4. stderr classification untuk operator guidance
5. healthcheck command per runtime
