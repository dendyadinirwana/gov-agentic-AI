# Publishing Checklist

## Before Publish
- [ ] Bundle manifest is complete and valid.
- [ ] Every cleaned document has a metadata companion.
- [ ] Classification and status are correct.
- [ ] Human reviewer is named.
- [ ] Publish targets match the document purpose.
- [ ] Sensitive content is masked or excluded as required.

## After Publish
- [ ] Update the target role's source map or policy map if the new material changes behavior.
- [ ] Move superseded material to `09-archive/` if needed.
- [ ] Re-run `python3 scripts/verify_knowledge_base.py`.
- [ ] Re-run `python3 scripts/generate_role_knowledge.py` without `--force` to refresh quality manifest safely.
