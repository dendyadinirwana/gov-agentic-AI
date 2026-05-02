#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / 'knowledge-base'
QUALITY = KB / 'knowledge_quality_manifest.json'
KB_MANIFEST = KB / 'kb_manifest.json'
DEFAULT_MD = ROOT / 'docs' / 'operations' / 'KNOWLEDGE_OPS_REPORT.md'
DEFAULT_JSON = ROOT / 'docs' / 'operations' / 'knowledge_ops_report.json'


READINESS_ORDER = {'seed': 0, 'usable': 1, 'operational': 2, 'high-confidence': 3}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def scan_bundles() -> list[dict[str, Any]]:
    bundles: list[dict[str, Any]] = []
    for role_dir in KB.glob('*/*/08-ingestion-ready'):
        manifest = role_dir / 'bundle.manifest.json'
        if not manifest.exists():
            continue
        try:
            data = load_json(manifest)
        except Exception as exc:
            bundles.append({
                'role_path': str(role_dir.relative_to(KB.parent / 'knowledge-base')).replace('/08-ingestion-ready',''),
                'bundle_dir': str(role_dir.relative_to(ROOT)),
                'bundle_id': 'invalid-json',
                'bundle_status': 'invalid',
                'document_count': 0,
                'error': str(exc),
            })
            continue
        bundles.append({
            'role_path': data.get('target_role_path', str(role_dir.parent.relative_to(KB))),
            'bundle_dir': str(role_dir.relative_to(ROOT)),
            'bundle_id': data.get('bundle_id', ''),
            'bundle_status': data.get('bundle_status', 'unknown'),
            'document_count': len(data.get('documents', [])),
            'prepared_by': data.get('prepared_by', ''),
            'human_reviewer': data.get('human_reviewer', ''),
        })
    return bundles


def build_report() -> dict[str, Any]:
    quality = load_json(QUALITY)
    roles = quality['roles']
    bundles = scan_bundles()

    weakest_roles = sorted(
        roles,
        key=lambda item: (item['average_score'], READINESS_ORDER.get(item['readiness'], -1), item['cluster'], item['alias'])
    )[:10]

    strongest_roles = sorted(
        roles,
        key=lambda item: (-item['average_score'], -READINESS_ORDER.get(item['readiness'], -1), item['cluster'], item['alias'])
    )[:10]

    candidates_for_high_confidence = []
    for role in roles:
        dims = role['dimensions']
        strong_dimensions = sum(1 for meta in dims.values() if meta['score'] >= 3)
        if role['readiness'] != 'high-confidence' and role['average_score'] >= 3.25 and strong_dimensions >= 6:
            weak_spots = [name for name, meta in dims.items() if meta['score'] < 4]
            candidates_for_high_confidence.append({
                'alias': role['alias'],
                'role': role['role'],
                'cluster': role['cluster'],
                'average_score': role['average_score'],
                'current_readiness': role['readiness'],
                'upgrade_levers': weak_spots[:3],
            })

    cluster_summary: dict[str, dict[str, Any]] = {}
    for role in roles:
        cluster = role['cluster']
        cluster_summary.setdefault(cluster, {'role_count': 0, 'avg_score_total': 0.0, 'readiness': {}})
        cluster_summary[cluster]['role_count'] += 1
        cluster_summary[cluster]['avg_score_total'] += role['average_score']
        cluster_summary[cluster]['readiness'][role['readiness']] = cluster_summary[cluster]['readiness'].get(role['readiness'], 0) + 1
    for cluster, item in cluster_summary.items():
        item['average_score'] = round(item.pop('avg_score_total') / item['role_count'], 2)

    pending_bundles = [b for b in bundles if b['bundle_status'] not in {'approved', 'published'}]
    review_ready_bundles = [b for b in bundles if b['bundle_status'] in {'review-ready', 'ready-for-review'}]

    return {
        'summary': quality['summary'],
        'role_count': len(roles),
        'high_confidence_candidates': candidates_for_high_confidence,
        'weakest_roles': weakest_roles,
        'strongest_roles': strongest_roles,
        'cluster_summary': cluster_summary,
        'bundle_summary': {
            'total_bundles': len(bundles),
            'pending_bundles': len(pending_bundles),
            'review_ready_bundles': len(review_ready_bundles),
            'approved_bundles': sum(1 for b in bundles if b['bundle_status'] == 'approved'),
            'published_bundles': sum(1 for b in bundles if b['bundle_status'] == 'published'),
        },
        'bundles': bundles,
        'recommended_next_actions': build_actions(quality['summary'], weakest_roles, pending_bundles, candidates_for_high_confidence),
    }


def build_actions(summary: dict[str, int], weakest_roles: list[dict[str, Any]], pending_bundles: list[dict[str, Any]], candidates: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    if weakest_roles:
        top = weakest_roles[0]
        actions.append(f"Deepen role-local sources and exemplars for {top['alias']} ({top['cluster']}) to improve its lowest-scoring dimensions.")
    if pending_bundles:
        actions.append('Review and either approve or reject pending ingestion bundles so institution documents can move into active knowledge folders.')
    if candidates:
        names = ', '.join(item['alias'] for item in candidates[:5])
        actions.append(f'Prioritize real approved source uploads for near-ready roles: {names}.')
    if summary.get('high_confidence', 0) < 5:
        actions.append('Increase the count of approved real-world policy sources and exemplar outputs to expand high-confidence coverage.')
    return actions


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Knowledge Ops Report')
    lines.append('')
    lines.append('## Summary')
    lines.append(f"- Role count: {report['role_count']}")
    s = report['summary']
    lines.append(f"- Readiness mix: high-confidence={s['high_confidence']}, operational={s['operational']}, usable={s['usable']}, seed={s['seed']}")
    b = report['bundle_summary']
    lines.append(f"- Ingestion bundles: total={b['total_bundles']}, pending={b['pending_bundles']}, review-ready={b['review_ready_bundles']}, approved={b['approved_bundles']}, published={b['published_bundles']}")
    lines.append('')

    lines.append('## Weakest Roles')
    for item in report['weakest_roles'][:5]:
        lines.append(f"- {item['alias']} — {item['role']} ({item['cluster']}) — score {item['average_score']} — {item['readiness']}")
    lines.append('')

    lines.append('## Strongest Roles')
    for item in report['strongest_roles'][:5]:
        lines.append(f"- {item['alias']} — {item['role']} ({item['cluster']}) — score {item['average_score']} — {item['readiness']}")
    lines.append('')

    lines.append('## High-Confidence Candidates')
    candidates = report['high_confidence_candidates'][:8]
    if candidates:
        for item in candidates:
            levers = ', '.join(item['upgrade_levers'])
            lines.append(f"- {item['alias']} ({item['cluster']}) — score {item['average_score']} — improve: {levers}")
    else:
        lines.append('- No near-ready candidates detected yet.')
    lines.append('')

    lines.append('## Cluster Summary')
    for cluster, item in sorted(report['cluster_summary'].items()):
        readiness_bits = ', '.join(f"{k}={v}" for k, v in sorted(item['readiness'].items()))
        lines.append(f"- {cluster}: roles={item['role_count']}, avg_score={item['average_score']}, {readiness_bits}")
    lines.append('')

    lines.append('## Pending Bundles')
    pending = [b for b in report['bundles'] if b['bundle_status'] not in {'approved', 'published'}]
    if pending:
        for item in pending[:10]:
            lines.append(f"- {item['bundle_id']} — {item['role_path']} — status={item['bundle_status']} — docs={item['document_count']}")
    else:
        lines.append('- No pending bundles detected.')
    lines.append('')

    lines.append('## Recommended Next Actions')
    for item in report['recommended_next_actions']:
        lines.append(f'- {item}')
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate a knowledge operations report for Gov-Agentic AI.')
    parser.add_argument('--json-out', default=str(DEFAULT_JSON), help='Path to write JSON report')
    parser.add_argument('--md-out', default=str(DEFAULT_MD), help='Path to write Markdown report')
    parser.add_argument('--stdout', action='store_true', help='Print Markdown summary to stdout')
    args = parser.parse_args()

    report = build_report()
    json_path = Path(args.json_out)
    md_path = Path(args.md_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + '\n')
    md_path.write_text(render_markdown(report) + '\n')
    print(f'json_report={json_path.relative_to(ROOT) if json_path.is_relative_to(ROOT) else json_path}')
    print(f'md_report={md_path.relative_to(ROOT) if md_path.is_relative_to(ROOT) else md_path}')
    print(f'role_count={report["role_count"]}')
    print(f'pending_bundles={report["bundle_summary"]["pending_bundles"]}')
    print(f'high_confidence_candidates={len(report["high_confidence_candidates"])}')
    if args.stdout:
        print('\n' + render_markdown(report))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
