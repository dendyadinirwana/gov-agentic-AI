from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from government_decision_engine import build_decision, load_registry, load_routing_policy


class DecisionEnginePolicyTests(unittest.TestCase):
    def test_registry_contains_declarative_policy_families(self) -> None:
        registry = load_registry()
        routing = load_routing_policy(registry)
        for key in [
            'intent_detection',
            'intent_primary_candidates',
            'review_role_by_cluster',
            'action_level_detection',
            'sensitivity_detection',
            'impact_detection',
            'work_state_policy',
        ]:
            self.assertIn(key, routing)

    def test_build_decision_uses_registry_backed_defaults(self) -> None:
        output = build_decision({
            'request_text': 'Bantu buat draft nota dinas untuk klarifikasi program dan siapkan review kepatuhan.',
            'evidence_complete': True,
            'approval_owner_known': True,
            'material_impact': True,
        })
        self.assertEqual(output['current_owner_role'], 'top-layer__gov-ai_yayak')
        self.assertEqual(output['intent_class'], 'draft-formal-artifact')
        self.assertEqual(output['action_level'], 'L3')
        self.assertEqual(output['work_state'], 'awaiting-approval')
        self.assertEqual(output['document_status'], 'review')


if __name__ == '__main__':
    unittest.main()
