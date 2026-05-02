#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'skills'
ROLE_SKILLS = SKILLS / 'roles'
MANIFEST = SKILLS / 'skill_manifest.json'
KB_MANIFEST = ROOT / 'knowledge-base' / 'kb_manifest.json'

FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.S)


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text()
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        result[key.strip()] = value.strip().strip('"')
    return result


def main() -> int:
    errors: list[str] = []
    if not MANIFEST.exists():
        errors.append('missing skills/skill_manifest.json')
        print_report(errors, 0, 0, 0, 0)
        return 1
    skill_manifest = json.loads(MANIFEST.read_text())
    kb_manifest = json.loads(KB_MANIFEST.read_text())
    skills = skill_manifest.get('skills', [])
    role_count = kb_manifest.get('role_count')
    skill_count = len(skills)
    if skill_count != role_count:
        errors.append(f'skill_count {skill_count} does not match role_count {role_count}')

    missing_skill_md = 0
    invalid_frontmatter = 0
    broken_reference_paths = 0

    shared_required = [
        'skills/_shared/gov-agentic-common/SKILL.md',
        'skills/_shared/gov-agentic-common/references/action-level-policy.md',
        'skills/_shared/gov-agentic-common/references/data-classification.md',
        'skills/_shared/gov-agentic-common/references/hitl-and-audit.md',
    ]
    for rel in shared_required:
        if not (ROOT / rel).exists():
            errors.append(f'missing shared file: {rel}')

    for item in skills:
        skill_md = ROOT / item['skill_md']
        skill_dir = ROOT / item['skill_path']
        if not skill_md.exists():
            missing_skill_md += 1
            errors.append(f'missing SKILL.md: {item["skill_md"]}')
            continue
        fm = parse_frontmatter(skill_md)
        if not fm.get('name') or not fm.get('description'):
            invalid_frontmatter += 1
            errors.append(f'invalid frontmatter: {item["skill_md"]}')
        if fm.get('name') != item.get('name'):
            invalid_frontmatter += 1
            errors.append(f'frontmatter name mismatch: {item["skill_md"]}')
        for rel in [
            'references/role-profile.md',
            'references/output-contract.md',
            'references/knowledge-map.md',
            'assets/.gitkeep',
            'scripts/.gitkeep',
        ]:
            if not (skill_dir / rel).exists():
                broken_reference_paths += 1
                errors.append(f'missing skill resource: {item["skill_path"]}/{rel}')
        for key in ['prompt_path', 'knowledge_path']:
            if not (ROOT / item[key]).exists():
                broken_reference_paths += 1
                errors.append(f'broken {key}: {item[key]}')
        shared_links = ROOT / item['knowledge_path'] / '_shared-links'
        if not shared_links.exists():
            broken_reference_paths += 1
            errors.append(f'missing shared links: {shared_links.relative_to(ROOT)}')
        for link in shared_links.iterdir() if shared_links.exists() else []:
            if link.is_symlink() and not link.exists():
                broken_reference_paths += 1
                errors.append(f'broken shared symlink: {link.relative_to(ROOT)}')

    print_report(errors, role_count, skill_count, missing_skill_md, invalid_frontmatter, broken_reference_paths)
    return 1 if errors else 0


def print_report(errors: list[str], role_count: int, skill_count: int, missing_skill_md: int, invalid_frontmatter: int, broken_reference_paths: int = 0) -> None:
    print(f'role_count={role_count}')
    print(f'skill_count={skill_count}')
    print(f'missing_skill_md={missing_skill_md}')
    print(f'invalid_frontmatter={invalid_frontmatter}')
    print(f'broken_reference_paths={broken_reference_paths}')
    print(f'errors={len(errors)}')
    for error in errors[:100]:
        print(f'ERROR: {error}')

if __name__ == '__main__':
    sys.exit(main())
