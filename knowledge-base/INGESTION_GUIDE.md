# Ingestion Guide

## Purpose
This guide explains the minimum contract for moving real institutional documents into the Gov-Agentic AI knowledge base safely.

## Minimum Metadata Per Document
- `title`
- `role_owner`
- `role_alias`
- `cluster`
- `document_type`
- `source_unit`
- `effective_date`
- `review_date`
- `classification` : `public | internal | restricted | sensitive`
- `status` : `draft | active | superseded | archived`
- `summary`
- `keywords`
- `human_reviewer`

## Checklist Before Entering `08-ingestion-ready`
- The document has been cleaned from empty pages, duplicate scans, or irrelevant content.
- The source version is identifiable and still valid enough to keep.
- A metadata `.json` companion has been filled.
- Sensitive content has been masked or excluded if the repository is not the correct canonical store.
- A human reviewer agrees the document is admissible as repository knowledge.

## Institution-Ready Bundle Workflow
1. Go to the target role's `08-ingestion-ready/` folder.
2. Copy `bundle.manifest.template.json` into `bundle.manifest.json`.
3. Put original files in `raw/`.
4. Put cleaned or OCR/index-ready files in `clean/`.
5. Add matching metadata files in `clean/`.
6. Run `python3 scripts/verify_ingestion_bundle.py <role>/08-ingestion-ready`.
7. After review, publish documents into the correct active knowledge folders.

## Publish Target Rules
- `01-source-documents`: primary evidence and canonical raw source material.
- `02-regulations-and-policies`: extracts, legal/policy notes, or rule-specific guidance.
- `03-templates-and-examples`: reusable templates and controlled examples.
- `04-sop-and-workflows`: approved workflow instructions only.
- `05-reference-data`: stable dictionaries, code lists, or lookup tables.
- `06-output-samples`: approved exemplar outputs.
- `08-ingestion-ready`: clean retrieval/index-ready copies, manifests, and intake traces.
- `09-archive`: superseded material with an archival reason.

## Validation Commands
- `python3 scripts/scaffold_ingestion_bundle.py <cluster/role_path>`
- `python3 scripts/verify_ingestion_bundle.py <cluster/role_path>/08-ingestion-ready`
- `python3 scripts/verify_knowledge_base.py`
- `python3 scripts/generate_role_knowledge.py`

- `python3 scripts/publish_ingestion_bundle.py <cluster/role_path>/08-ingestion-ready --dry-run`
