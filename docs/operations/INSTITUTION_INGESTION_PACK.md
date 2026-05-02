# Institution-Ready Ingestion Pack

## Purpose
This pack turns the repository into a practical onboarding surface for real agency documents. Teams can prepare an intake bundle, validate it, then publish approved material into the correct role folders without guessing placement rules.

## Standard Bundle Shape
- `raw/` : original files from the institution
- `clean/` : cleaned/index-ready derivative files
- `bundle.manifest.json` : bundle-level publishing contract
- `*.metadata.json` : document metadata companions
- `publish-checklist.md` : reviewer checklist before publish

## Recommended Workflow
1. Copy the role's `bundle.manifest.template.json` and rename it to `bundle.manifest.json`.
2. Put original files in `08-ingestion-ready/raw/`.
3. Put cleaned files and metadata in `08-ingestion-ready/clean/`.
4. Run `python3 scripts/verify_ingestion_bundle.py <role>/08-ingestion-ready`.
5. After human review, publish the approved files into `01-source-documents`, `02-regulations-and-policies`, `03-templates-and-examples`, `06-output-samples`, or keep a retrieval copy in `08-ingestion-ready`.
6. Re-run `python3 scripts/verify_knowledge_base.py` and `python3 scripts/generate_role_knowledge.py`.

## Publish Target Rules
- `01-source-documents`: primary evidence, raw or canonical source material.
- `02-regulations-and-policies`: extracts, policy notes, or rule-specific guidance.
- `03-templates-and-examples`: reusable templates and controlled examples.
- `04-sop-and-workflows`: approved workflow instructions only.
- `05-reference-data`: stable dictionaries, code lists, or lookup tables.
- `06-output-samples`: approved exemplar outputs.
- `08-ingestion-ready`: cleaned/index-ready copies, manifests, metadata, and intake traces.
- `09-archive`: superseded content with archive reason.

## Minimum Metadata Contract
- `title`
- `role_owner`
- `role_alias`
- `cluster`
- `document_type`
- `source_unit`
- `effective_date`
- `review_date`
- `classification`
- `status`
- `summary`
- `keywords`
- `human_reviewer`

## Safety Rules
- Never publish unclear or ownerless content as canonical knowledge.
- Never put sensitive material in the repo if the proper controlled system should hold it instead.
- Do not overwrite current active knowledge without archiving or version rationale.
- Keep bundle verification evidence so maintainers can explain why a document was admitted.


## Semi-Automated Publish
Once a bundle is reviewed and its `bundle_status` is set to `approved`, you can publish it with:

- `python3 scripts/publish_ingestion_bundle.py knowledge-base/<cluster>/<role>/08-ingestion-ready --dry-run`
- `python3 scripts/publish_ingestion_bundle.py knowledge-base/<cluster>/<role>/08-ingestion-ready --archive-existing --refresh-quality`

### Publish Safety Rules
- The publisher only accepts bundles with `bundle_status: approved`.
- Each document must have `publish_status: approved` or `ready`.
- Existing target files are only replaced when `--archive-existing` is set.
- Replaced files are moved into the role's `09-archive/` folder.
- Use `--dry-run` first for every new batch.
