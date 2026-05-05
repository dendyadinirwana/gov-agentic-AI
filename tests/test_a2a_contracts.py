from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from a2a_contracts import validate_handoff, validate_response, validate_terminal_state, validate_audit_event

ORCHESTRATOR = ROOT / 'scripts' / 'agent_to_agent_orchestrator.py'
ADAPTER = ROOT / 'scripts' / 'role_runtime_adapter.py'
EXAMPLE = ROOT / 'examples' / 'agent-to-agent' / 'yayak-alfian-edi.request.json'


class A2AContractTests(unittest.TestCase):
    def test_orchestrator_output_matches_contract_shape(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), '--input-json', str(EXAMPLE)],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload['contract_version'], 'a2a.v1')
        self.assertEqual(payload['workflow_state']['current_owner_role'], 'top-layer__gov-ai_yayak')
        self.assertEqual(len(payload['steps']), 2)
        self.assertEqual(payload['steps'][0]['handoff']['to_role'], 'komunikasi-dan-dokumen__penulis-naskah_alfian')
        self.assertEqual(payload['steps'][1]['handoff']['to_role'], 'kebijakan-dan-hukum__monitor-kepatuhan-hukum_edi')
        self.assertFalse(validate_handoff(payload['steps'][0]['handoff']))
        self.assertFalse(validate_response(payload['steps'][0]['response'], payload['steps'][0]['handoff']))
        self.assertFalse(validate_terminal_state(payload['final'], payload['trace_id']))
        event_types = {event['event_type'] for event in payload['audit_events']}
        self.assertIn('governance_gate_triggered', event_types)
        self.assertIn('human_touchpoint_required', event_types)
        self.assertIn('review_returned', event_types)
        severities = {event['event_type']: event['severity'] for event in payload['audit_events']}
        self.assertEqual(severities['handoff_created'], 'info')
        self.assertEqual(severities['governance_gate_triggered'], 'warning')
        self.assertEqual(severities['review_returned'], 'warning')
        for event in payload['audit_events']:
            self.assertFalse(validate_audit_event(event, payload['trace_id']))

    def test_real_adapter_without_command_falls_back_cleanly(self) -> None:
        handoff = {
            'contract_version': 'a2a.v1',
            'trace_id': 'trace-test-fallback',
            'handoff_id': 'handoff-test-fallback',
            'from_role': 'top-layer__gov-ai_yayak',
            'to_role': 'komunikasi-dan-dokumen__penulis-naskah_alfian',
            'intent_class': 'draft-formal-artifact',
            'task_summary': 'Buat draft formal awal.',
            'action_level': 'L3',
            'workflow_state': {
                'trace_id': 'trace-test-fallback',
                'intent_class': 'draft-formal-artifact',
                'work_state': 'awaiting-approval',
                'current_owner_role': 'top-layer__gov-ai_yayak',
                'next_owner_role': 'komunikasi-dan-dokumen__penulis-naskah_alfian',
                'action_level': 'L3',
                'document_status': 'review',
                'human_touchpoint_required': True,
            },
            'payload': {
                'request_text': 'Tolong buat draf nota dinas.',
                'evidence_sources': ['memo internal'],
                'assumptions': [],
            },
            'governance': {
                'decision_gate': 'REVIEW_NEEDED',
                'decision_reason': 'human approval required',
                'human_touchpoint_required': True,
                'approval_gate': 'human accountable owner',
                'stop_condition': None,
            },
            'audit': {
                'created_at': '2026-05-05T00:00:00+00:00',
                'created_by': 'top-layer__gov-ai_yayak',
                'sequence': 1,
            },
        }
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as fh:
            fh.write(json.dumps(handoff, ensure_ascii=False))
            temp_path = fh.name
        try:
            result = subprocess.run(
                [sys.executable, str(ADAPTER), '--input-json', temp_path, '--adapter-mode', 'hermes-real', '--runtime-config', str(ROOT / 'configs' / 'runtime.generated.json')],
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload['role_slug'], 'komunikasi-dan-dokumen__penulis-naskah_alfian')
            self.assertIn(payload['adapter_execution']['mode'], {'hermes-mock', 'hermes-real'})
            self.assertTrue(payload['adapter_execution'].get('audit_hints', {}).get('fallback_used', False) or payload['adapter_execution']['mode'] == 'hermes-real')
            self.assertFalse(validate_response(payload, handoff))
        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
