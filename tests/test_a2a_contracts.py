from __future__ import annotations

import json
import os
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
EXAMPLES = ROOT / 'examples' / 'agent-to-agent'
EXAMPLE = EXAMPLES / 'yayak-alfian-edi.request.json'
FIXTURE_CASES = [
    {
        'file': 'yayak-alfian-edi.request.json',
        'expected_steps': 2,
        'expected_path': ['Alfian', 'Edi'],
        'expected_status': 'needs_review',
        'expected_event_types': {'governance_gate_triggered', 'human_touchpoint_required', 'review_returned'},
    },
    {
        'file': 'budget-review.request.json',
        'expected_steps': 1,
        'expected_path': ['Anastasia'],
        'expected_status': 'completed',
        'expected_event_types': {'handoff_created', 'role_response_recorded', 'workflow_terminalized'},
    },
    {
        'file': 'procurement-neutrality.request.json',
        'expected_steps': 1,
        'expected_path': ['Hafidus'],
        'expected_status': 'completed',
        'expected_event_types': {'handoff_created', 'role_response_recorded', 'workflow_terminalized'},
    },
    {
        'file': 'archive-record.request.json',
        'expected_steps': 2,
        'expected_path': ['Sovia', 'Izza'],
        'expected_status': 'completed',
        'expected_event_types': {'handoff_created', 'role_response_recorded', 'workflow_terminalized'},
    },
    {
        'file': 'escalation-blocker.request.json',
        'expected_steps': 1,
        'expected_path': ['Winda'],
        'expected_status': 'needs_review',
        'expected_event_types': {'handoff_created', 'role_response_recorded', 'human_touchpoint_required', 'workflow_terminalized'},
    },
    {
        'file': 'retrieval-budget-review.request.json',
        'expected_steps': 1,
        'expected_path': ['Anastasia'],
        'expected_status': 'completed',
        'expected_event_types': {'handoff_created', 'role_response_recorded', 'workflow_terminalized'},
    },
]


class A2AContractTests(unittest.TestCase):
    def test_orchestrator_fixture_matrix_matches_contract_shape(self) -> None:
        for case in FIXTURE_CASES:
            with self.subTest(case=case['file']):
                result = subprocess.run(
                    [sys.executable, str(ORCHESTRATOR), '--input-json', str(EXAMPLES / case['file'])],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                payload = json.loads(result.stdout)
                self.assertEqual(payload['contract_version'], 'a2a.v1')
                self.assertEqual(payload['workflow_state']['current_owner_role'], 'top-layer__gov-ai_yayak')
                self.assertEqual(len(payload['steps']), case['expected_steps'])
                self.assertEqual(payload['final']['execution_path'], case['expected_path'])
                self.assertEqual(payload['final']['final_status'], case['expected_status'])
                if payload['steps']:
                    self.assertFalse(validate_handoff(payload['steps'][0]['handoff']))
                    self.assertFalse(validate_response(payload['steps'][0]['response'], payload['steps'][0]['handoff']))
                self.assertFalse(validate_terminal_state(payload['final'], payload['trace_id']))
                event_types = {event['event_type'] for event in payload['audit_events']}
                self.assertTrue(case['expected_event_types'].issubset(event_types))
                event_policies = {event['event_type']: event for event in payload['audit_events']}
                self.assertEqual(event_policies['handoff_created']['severity'], 'info')
                self.assertEqual(event_policies['handoff_created']['retention_class'], 'operational_record')
                self.assertEqual(event_policies['handoff_created']['compliance_class'], 'standard')
                self.assertEqual(event_policies['handoff_created']['response_policy'], 'log_only')
                if 'governance_gate_triggered' in event_policies:
                    self.assertEqual(event_policies['governance_gate_triggered']['severity'], 'warning')
                    self.assertEqual(event_policies['governance_gate_triggered']['retention_class'], 'governance_record')
                    self.assertEqual(event_policies['governance_gate_triggered']['compliance_class'], 'governance_control')
                    self.assertEqual(event_policies['governance_gate_triggered']['response_policy'], 'review_required')
                if 'review_returned' in event_policies:
                    self.assertEqual(event_policies['review_returned']['compliance_class'], 'human_approval')
                    self.assertEqual(event_policies['review_returned']['response_policy'], 'review_required')
                if case['file'] == 'retrieval-budget-review.request.json':
                    self.assertTrue(payload['final']['retrieval']['required'])
                    self.assertEqual(payload['final']['retrieval']['provider'], 'local-json-corpus')
                    self.assertGreater(payload['final']['retrieval']['hit_count'], 0)
                    self.assertGreater(len(payload['steps'][0]['response']['evidence_map']), 0)
                    self.assertEqual(payload['steps'][0]['response']['evidence_map'][0]['use'], 'retrieved evidence')
                    self.assertIn('source_id', payload['steps'][0]['response']['evidence_map'][0])
                for event in payload['audit_events']:
                    self.assertFalse(validate_audit_event(event, payload['trace_id']))

    def _sample_handoff(self, trace_id: str = 'trace-test-fallback') -> dict:
        return {
            'contract_version': 'a2a.v1',
            'trace_id': trace_id,
            'handoff_id': 'handoff-test-fallback',
            'from_role': 'top-layer__gov-ai_yayak',
            'to_role': 'komunikasi-dan-dokumen__penulis-naskah_alfian',
            'intent_class': 'draft-formal-artifact',
            'task_summary': 'Buat draft formal awal.',
            'action_level': 'L3',
            'workflow_state': {
                'trace_id': trace_id,
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

    def test_real_adapter_without_command_falls_back_cleanly(self) -> None:
        handoff = self._sample_handoff()
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

    def test_real_adapter_normalizes_json_object_output(self) -> None:
        handoff = self._sample_handoff('trace-test-runtime-json')
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as fh:
            fh.write(json.dumps(handoff, ensure_ascii=False))
            temp_path = fh.name
        env = os.environ.copy()
        env['GOV_AGENTIC_HERMES_ROLE_CMD'] = f'"{sys.executable}" "{ROOT / "scripts" / "runtime_wrapper_example.py"}" --runtime hermes --handoff $handoff_path --role $role_slug --trace $trace_id'
        try:
            result = subprocess.run(
                [sys.executable, str(ADAPTER), '--input-json', temp_path, '--adapter-mode', 'hermes-real', '--runtime-config', str(ROOT / 'configs' / 'runtime.generated.json')],
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload['adapter_execution']['mode'], 'hermes-real')
            self.assertEqual(payload['adapter_execution']['details']['normalized_from'], 'json-object')
            self.assertIn('--handoff', payload['adapter_execution']['runtime_contract']['resolved_command'])
            self.assertEqual(payload['adapter_execution']['runtime_contract']['command_source'], 'env:GOV_AGENTIC_HERMES_ROLE_CMD')
            self.assertFalse(validate_response(payload, handoff))
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_real_adapter_timeout_returns_reviewable_response(self) -> None:
        handoff = self._sample_handoff('trace-test-runtime-timeout')
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as fh:
            fh.write(json.dumps(handoff, ensure_ascii=False))
            temp_path = fh.name
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as cfg:
            cfg.write(json.dumps({
                'a2a_adapter_execution': {
                    'prefer_real_runtime': False,
                    'modes': {
                        'hermes-real': {
                            'command': f"{sys.executable} -c \"import time; time.sleep(2)\"",
                            'timeout_seconds': 1,
                            'stdout_contract': 'a2a-response-json|json-object|plain-text'
                        }
                    }
                }
            }))
            cfg_path = cfg.name
        try:
            result = subprocess.run(
                [sys.executable, str(ADAPTER), '--input-json', temp_path, '--adapter-mode', 'hermes-real', '--runtime-config', cfg_path],
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload['status'], 'needs_review')
            self.assertEqual(payload['adapter_execution']['mode'], 'hermes-real')
            self.assertEqual(payload['adapter_execution']['runtime_behavior'], 'real-runtime-command-timeout')
            self.assertTrue(payload['adapter_execution']['audit_hints']['runtime_timeout'])
            self.assertEqual(payload['adapter_execution']['runtime_contract']['command_source'], 'config.command')
            self.assertFalse(validate_response(payload, handoff))
        finally:
            Path(temp_path).unlink(missing_ok=True)
            Path(cfg_path).unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
