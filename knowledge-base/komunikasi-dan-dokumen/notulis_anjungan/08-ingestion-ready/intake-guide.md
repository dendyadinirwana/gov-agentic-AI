# Intake Guide — Notulis (Anjungan)

## What New Knowledge Belongs Here
- New official documents directly used by notulis.
- Role-local SOP refinements and approved workflow notes.
- Approved templates and high-quality output exemplars.
- Stable reference tables needed repeatedly by this role.

## Minimum Intake Metadata
- document_title
- issuing_owner
- issue_date
- revision_or_version
- source_type
- classification
- role_relevance
- review_status

## Ingestion Steps
1. Put raw source material in the semantically correct folder.
2. Add provenance metadata using the templates already in this directory.
3. Update `source-map.md`, `policy-map.md`, or `artifact-catalog.md` when the new material changes how the role should work.
4. Move superseded material to `../09-archive` with a short reason.

## Do Not Ingest
- Unsourced copied text
- Personal notes without institutional value
- Drafts that have no owner or review path
- Sensitive data that should stay in a protected system instead of the repo
