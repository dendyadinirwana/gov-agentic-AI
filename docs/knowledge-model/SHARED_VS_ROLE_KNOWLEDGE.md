# Shared vs Role Knowledge

## Shared Knowledge
Use `knowledge-base/_shared` for knowledge reused by many roles:
- general regulations
- global SOPs
- organization-wide templates
- data dictionaries
- compliance/audit references
- canonical golden outputs

## Role Knowledge
Use role folders for:
- role-specific source documents
- role-specific examples and outputs
- review notes unique to the role
- ingestion-ready files already curated for that role

## Rule
If 3 or more roles will use the same source, prefer placing it under `_shared` and linking it from the role folders.
