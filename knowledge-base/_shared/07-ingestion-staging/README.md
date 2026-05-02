# 07-ingestion-staging

Use this staging area for institution-ready knowledge bundles before they are published into role folders.

## Intended Flow
1. Create a bundle folder per intake batch.
2. Put raw files under `raw/`.
3. Put cleaned/index-ready files under `clean/`.
4. Fill `bundle.manifest.json`.
5. Run `python3 scripts/verify_ingestion_bundle.py <bundle-dir>`.
6. After human review, move the approved outputs into the target role's `08-ingestion-ready/` or target knowledge folders.
