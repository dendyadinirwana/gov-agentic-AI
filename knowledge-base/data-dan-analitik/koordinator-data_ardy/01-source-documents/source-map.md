# Source Map — Koordinator Data (Ardy)

## Source Priority Rules
1. Start from the actual dataset, metadata, ownership, schema meaning, and intended use case.
2. Use the implementation pack governance and data-owner model to ensure the right source owner and access basis are visible.
3. Treat data readiness as valid only when provenance, structure, and usage constraints are explicit.
4. If the data request is sensitive, under-documented, or structurally ambiguous, hold before downstream analytics continue.

## Canonical vs Supporting Sources
- Canonical: owned datasets, official metadata, schema definitions, source-system notes, approved data-owner guidance.
- Supporting: analyst notes, previous extracts, working spreadsheets, mapping tables.
- Non-authoritative: CSVs with unknown origin, copied fields with no definition, or dataset summaries that hide missing owner/context.

## Mandatory Shared Directories
- `../_shared-links/00-governance-and-routing`
- `../_shared-links/04-data-dictionaries`
- `../_shared-links/05-risk-and-compliance`
- `../_shared-links/06-audit-and-observability`

## Data-Coordination Source Inventory
- Implementation pack data-owner and knowledge-steward concepts apply strongly here.
- Ardy prepares dataset readiness and routing for Hanan/Varin or other downstream consumers.
