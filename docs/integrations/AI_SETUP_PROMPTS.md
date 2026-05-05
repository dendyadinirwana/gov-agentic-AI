# AI Setup Prompts for Gov-Agentic AI

Dokumen ini berisi **prompt siap copy-paste** untuk meminta AI coding agent melakukan setup, update, atau validasi repo **Gov-Agentic AI** dari GitHub.

Fokus dokumen ini bukan membuat installer shell tunggal, tetapi memberi **prompt operasional** yang memaksa agent bekerja rapi:

1. clone atau update repo,
2. inspect struktur repo dulu,
3. install dependency minimum yang benar-benar dibutuhkan,
4. jalankan validasi inti,
5. laporkan hasil secara jelas.

---

## Prinsip penggunaan

Gunakan prompt ini kalau lo ingin agent:
- setup repo dari nol,
- update local clone yang sudah ada,
- validasi repo tanpa menyentuh kode,
- atau melakukan setup dengan konteks runtime tertentu seperti **Hermes** atau **OpenClaw**.

Pola kerja yang diharapkan selalu sama:

**clone/update -> inspect -> install minimum deps -> validate -> report**

Bukan:

**clone -> install random package -> bilang beres**

---

## Repo context yang sebaiknya dipahami agent

Sebelum menjalankan prompt, anggap repo ini sebagai:
- governed **agent-to-agent orchestration MVP**,
- fokus pada workflow pemerintah / public-sector knowledge work,
- punya jalur **retrieval grounding**,
- punya jalur **HITL review**,
- dan validasi utamanya ada di script smoke test + unit test, bukan di frontend app.

Kalau perlu, tambahkan preamble ini ke prompt:

```text
Context:
This repository is a governed government-oriented agent-to-agent orchestration MVP. Treat it as a workflow/runtime validation repo, not as a generic web application. Prioritize contract validation, smoke tests, retrieval-backed examples, and HITL review flow.
```

---

## Kapan pakai prompt yang mana

### 1. Fresh clone setup
Pakai saat:
- repo belum ada di local machine,
- atau lo ingin agent clone ke path baru lalu setup dari nol.

### 2. Update existing clone
Pakai saat:
- repo sudah ada,
- lo ingin agent pull/update lalu validasi lagi.

### 3. Validate only
Pakai saat:
- repo sudah ada dan dependency kemungkinan sudah terpasang,
- lo cuma mau tahu masih sehat atau tidak.

### 4. Hermes-specific setup
Pakai saat:
- agent yang menjalankan pekerjaan ini adalah Hermes,
- dan lo mau dia setup repo dengan cara yang cocok untuk workflow Hermes.

### 5. OpenClaw-specific setup
Pakai saat:
- agent yang menjalankan pekerjaan ini adalah OpenClaw-style environment,
- dan lo mau dia tetap setup repo dengan pendekatan konservatif dan bisa diverifikasi.

---

## Standard validation target

Prompt-prompt di bawah ini menganggap validasi minimum repo adalah:

```bash
python3 scripts/verify_repo.py
python3 scripts/smoke_test_agent_to_agent.py
python3 scripts/smoke_test_agent_to_agent_matrix.py
python3 -m unittest discover -s tests -v
```

Kalau agent mengklaim setup selesai tanpa menjalankan minimal flow ini, anggap setup-nya belum sah.

---

## Prompt 1 — Fresh clone setup

Gunakan ini untuk clone + setup dari nol.

```text
You are operating a local AI coding agent on my machine.

Task:
Clone, set up, and validate the Gov-Agentic AI repository from GitHub as a runnable MVP orchestration environment.

Repository:
<PASTE_GITHUB_REPO_URL_HERE>

Objectives:
- clone the repository locally
- inspect the repository before installing anything
- identify the minimum dependencies required
- install only the necessary dependencies
- run the repository validation flow
- produce a clear setup report

Rules:
1. Do not assume a package manager or installer unless the repo actually defines one.
2. Inspect the repository structure and README first.
3. Prefer minimal and reversible setup steps.
4. Avoid unnecessary global installs.
5. Do not modify application logic unless setup is blocked and the fix is explicitly justified.
6. Do not claim success without verification.

Required workflow:
1. Clone the repository.
2. Read the README and inspect key project files.
3. Identify runtime requirements.
4. Install the minimum required dependencies.
5. Run the validation flow.
6. Report the final result clearly.

Required validation flow:
- python3 scripts/verify_repo.py
- python3 scripts/smoke_test_agent_to_agent.py
- python3 scripts/smoke_test_agent_to_agent_matrix.py
- python3 -m unittest discover -s tests -v

Nice-to-have validation:
- run a retrieval-backed example
- run a HITL example through packet and decision flow

Return output in this format:
- Repository URL:
- Local path:
- Setup method used:
- Dependencies installed:
- Commands executed:
- Validation results:
- Retrieval example status:
- HITL example status:
- Issues or risks:
- Recommended next step:
```

---

## Prompt 2 — Update existing local clone

Gunakan ini kalau repo sudah ada di local.

```text
You are operating a local AI coding agent on my machine.

Task:
Update and re-validate the existing local Gov-Agentic AI repository.

Repository URL:
<PASTE_GITHUB_REPO_URL_HERE>

Expected local path:
<PASTE_LOCAL_PATH_HERE>

Objectives:
- confirm whether the repo already exists locally
- update it cleanly instead of creating duplicate clones
- inspect the current repo state before making changes
- refresh only what is needed
- re-run the validation flow
- report the result

Rules:
1. If the repository already exists locally, update it instead of cloning a second copy.
2. Inspect git status before making changes.
3. Do not overwrite uncommitted local work without reporting it.
4. Install dependencies only if validation shows something is missing.
5. Do not claim success without verification.

Required workflow:
1. Check whether the repo exists at the expected local path.
2. Inspect git status and branch state.
3. Pull or update the repository conservatively.
4. Re-check whether dependency changes are required.
5. Run the validation flow.
6. Report outcomes and any local divergence.

Required validation flow:
- python3 scripts/verify_repo.py
- python3 scripts/smoke_test_agent_to_agent.py
- python3 scripts/smoke_test_agent_to_agent_matrix.py
- python3 -m unittest discover -s tests -v

Return output in this format:
- Repository URL:
- Local path:
- Repo status before update:
- Update method used:
- Dependencies installed or updated:
- Commands executed:
- Validation results:
- Uncommitted local changes found:
- Issues or risks:
- Recommended next step:
```

---

## Prompt 3 — Validate only

Gunakan ini kalau repo sudah terpasang dan lo cuma mau cek sehat/tidak.

```text
You are operating a local AI coding agent on my machine.

Task:
Validate the current Gov-Agentic AI repository without changing repo logic.

Repository local path:
<PASTE_LOCAL_PATH_HERE>

Objectives:
- inspect the repo state
- run validation only
- identify missing dependencies or broken flows
- report what passes and what fails

Rules:
1. Do not change repository logic.
2. Do not install large or unrelated dependencies unless clearly required for validation.
3. If a dependency is missing, report it explicitly before making broad environment changes.
4. Do not claim success without verification.

Required validation flow:
- python3 scripts/verify_repo.py
- python3 scripts/smoke_test_agent_to_agent.py
- python3 scripts/smoke_test_agent_to_agent_matrix.py
- python3 -m unittest discover -s tests -v

Optional deeper validation:
- run retrieval-backed example
- run HITL packet/decision/resume flow

Return output in this format:
- Local path:
- Repo status:
- Commands executed:
- Validation results:
- Missing dependency or environment gaps:
- Risks:
- Recommended next step:
```

---

## Prompt 4 — Hermes-specific setup

Gunakan ini kalau target agent-nya Hermes.

```text
You are operating Hermes Agent on my machine.

Task:
Set up and validate the Gov-Agentic AI repository from GitHub as a runnable MVP orchestration environment.

Repository:
<PASTE_GITHUB_REPO_URL_HERE>

Requirements:
1. Clone the repository if missing, or update it if already present.
2. Read the README and inspect project structure first.
3. Identify the minimum dependencies required to run the repo validation flow.
4. Install only the necessary dependencies.
5. Run the validation flow.
6. Confirm whether retrieval-backed and HITL-backed example flows are runnable.
7. Do not fabricate success. Verify every claim.

Validation flow:
- python3 scripts/verify_repo.py
- python3 scripts/smoke_test_agent_to_agent.py
- python3 scripts/smoke_test_agent_to_agent_matrix.py
- python3 -m unittest discover -s tests -v

Constraints:
- prefer minimal setup
- avoid unnecessary global changes
- explain any dependency inference conservatively
- do not claim success without verification

Return output in this format:
- Repository URL:
- Local path:
- Repo status (cloned or updated):
- Dependencies installed:
- Commands executed:
- Validation results:
- Retrieval example status:
- HITL example status:
- Remaining issues:
- Recommended next step:
```

---

## Prompt 5 — OpenClaw-specific setup

Gunakan ini kalau target agent-nya OpenClaw-style environment.

```text
You are operating an OpenClaw-style local coding agent.

Task:
Clone, prepare, and validate the Gov-Agentic AI repository from GitHub.

Repository:
<PASTE_GITHUB_REPO_URL_HERE>

Requirements:
1. Clone or update the repository locally.
2. Inspect the README and repo structure before making changes.
3. Determine the minimum setup needed to run the repository’s MVP validation flow.
4. Install only required dependencies.
5. Run the validation scripts and confirm the results.
6. Preserve existing local work if the repo already exists.
7. Do not claim success without verification.

Validation flow:
- python3 scripts/verify_repo.py
- python3 scripts/smoke_test_agent_to_agent.py
- python3 scripts/smoke_test_agent_to_agent_matrix.py
- python3 -m unittest discover -s tests -v

Return output in this format:
- Repository URL:
- Local path:
- Repo status:
- Setup method used:
- Dependencies installed:
- Commands executed:
- Validation results:
- Issues found:
- Next actions:
```

---

## Prompt 6 — Retrieval + HITL deep verification

Gunakan ini kalau setup dasar sudah lolos dan lo mau agent ngetes jalur yang lebih representatif.

```text
You are operating a local AI coding agent on my machine.

Task:
Run deeper workflow verification for the Gov-Agentic AI repository after base setup has already succeeded.

Repository local path:
<PASTE_LOCAL_PATH_HERE>

Objectives:
- confirm retrieval-backed orchestration is runnable
- confirm HITL review packet/decision/resume flow is runnable
- report the results in a concise but verifiable way

Rules:
1. Do not modify application logic unless verification is blocked and the reason is explicitly explained.
2. Keep all outputs inspectable.
3. Do not claim success without command-level verification.

Required workflow:
1. Run the retrieval-backed example.
2. Run the HITL example until it reaches needs_review.
3. Generate a review packet.
4. Generate a review decision.
5. Resume the orchestrator with that review decision.
6. Report all command outputs and final statuses.

Return output in this format:
- Retrieval example command(s):
- Retrieval example result:
- HITL workflow command(s):
- Review packet result:
- Review decision result:
- Resume result:
- Final status summary:
- Risks or gaps:
```

---

## Prompt 7 — Conservative fix-setup mode

Gunakan ini kalau setup gagal dan lo mau agent memperbaiki environment **tanpa langsung ngacak-ngacak repo**.

```text
You are operating a local AI coding agent on my machine.

Task:
Diagnose and fix setup blockers for the Gov-Agentic AI repository conservatively.

Repository local path:
<PASTE_LOCAL_PATH_HERE>

Objectives:
- identify why validation fails
- prefer environment fixes over unnecessary repo logic edits
- apply the smallest safe fix
- re-run validation
- report exactly what changed

Rules:
1. Diagnose first, change later.
2. Prefer fixing missing dependencies, interpreter issues, or execution assumptions before editing repository code.
3. If code changes become necessary, explain why setup could not proceed without them.
4. Do not claim success without re-running validation.

Required validation flow after each meaningful fix:
- python3 scripts/verify_repo.py
- python3 scripts/smoke_test_agent_to_agent.py
- python3 scripts/smoke_test_agent_to_agent_matrix.py
- python3 -m unittest discover -s tests -v

Return output in this format:
- Root cause:
- Fix category (environment or code):
- Files changed:
- Dependencies installed:
- Commands executed:
- Validation results after fix:
- Remaining issues:
```

---

## Rekomendasi praktis

Kalau lo mau paling efisien, pakai urutan ini:

### Fresh machine
1. Prompt 1 — Fresh clone setup
2. Kalau gagal, Prompt 7 — Conservative fix-setup mode
3. Kalau setup dasar lolos, Prompt 6 — Retrieval + HITL deep verification

### Existing machine
1. Prompt 2 — Update existing local clone
2. Kalau cuma mau health check, Prompt 3 — Validate only
3. Kalau perlu pembuktian workflow, Prompt 6

### Runtime-specific execution
- pakai Prompt 4 untuk Hermes
- pakai Prompt 5 untuk OpenClaw

---

## Output quality rule

Output agent dianggap bagus kalau:
- menyebut **path lokal repo**,
- menyebut **dependency yang benar-benar diinstall**,
- menyebut **command yang dijalankan**,
- menyebut **hasil validasi per langkah**,
- dan **tidak ngaku sukses tanpa bukti**.

Kalau output agent cuma bilang “setup completed” tanpa command dan tanpa hasil validasi, anggap itu belum cukup.

---

## Related repo docs

Untuk memahami repo yang sedang di-setup, lihat juga:
- `README.md`
- `docs/architecture/AGENT_TO_AGENT_CONTRACTS_AND_RUNTIME.md`
- `docs/architecture/A2A_RUNTIME_HARDENING.md`
- `docs/architecture/A2A_RETRIEVAL_INTEGRATION.md`
- `docs/architecture/A2A_HITL_REVIEW_CONSOLE.md`
- `docs/architecture/GOVERNMENT_WORK_LOGIC.md`

---

## Suggested future extension

Kalau nanti mau, dokumen ini bisa diperluas lagi dengan:
- prompt khusus **GitHub Codespaces / cloud runner**,
- prompt khusus **non-interactive CI verification**,
- prompt khusus **repo cleanup + revalidation**,
- prompt khusus **install + attach shared skills for Hermes/OpenClaw**.
