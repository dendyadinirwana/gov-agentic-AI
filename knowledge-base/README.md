# Knowledge Base Structure

Folder ini adalah struktur knowledge base per role untuk Gov Agentic AI.

## Prinsip
- Satu role punya satu folder knowledge utama.
- Dokumen mentah masuk ke `01-source-documents`.
- Dokumen yang siap diindeks/RAG masuk ke `08-ingestion-ready`.
- Template, SOP, contoh output, dan reference dipisahkan agar retrieval lebih presisi.
- Simpan file dengan nama yang konsisten: `YYYY-MM-DD_topik_versi.ext` bila memungkinkan.

## Struktur Umum per Role
- `00-readme` : konteks role, prioritas knowledge, aturan penggunaan.
- `01-source-documents` : dokumen mentah hasil upload/ekspor.
- `02-regulations-and-policies` : regulasi, SOP, kebijakan, dasar hukum.
- `03-templates-and-examples` : template aktif dan contoh final yang baik.
- `04-sop-and-workflows` : alur kerja operasional per role.
- `05-reference-data` : kamus data, lookup table, daftar indikator, daftar unit.
- `06-output-samples` : contoh jawaban/artefak final per role.
- `07-review-notes` : catatan reviewer, red flags, dan lesson learned.
- `08-ingestion-ready` : versi bersih/terstruktur untuk indexing dan retrieval.
- `09-archive` : dokumen lama, superseded, atau tidak aktif.

## File Index Global
- `knowledge-base/ROLE_INDEX.md` : daftar seluruh role dan foldernya.
- `knowledge-base/INGESTION_GUIDE.md` : aturan ingest dan metadata minimum.
