#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / 'configs'
PROMPTS = ROOT / 'prompts' / 'system'
OUT_SCHEMA = ROOT / 'schemas' / 'government_workflow_state.schema.json'

INTENT_RULES = {
    'route-intake': ['bantu', 'arahkan', 'klasifikasi', 'status', 'proses', 'langkah'],
    'check-completeness': ['lengkap', 'kelengkapan', 'cek dokumen', 'missing', 'lampiran'],
    'draft-formal-artifact': ['draft', 'buat surat', 'nota dinas', 'memo', 'kak', 'tor', 'rab'],
    'review-compliance': ['audit', 'kepatuhan', 'compliance', 'bukti', 'trace', 'red flag'],
    'review-legal-risk': ['kontrak', 'mou', 'pks', 'legal', 'klausul', 'sengketa', 'kewenangan'],
    'review-budget-fit': ['anggaran', 'rab', 'sbm', 'pagu', 'biaya', 'akun belanja'],
    'review-specification-neutrality': ['spesifikasi', 'spek', 'sni', 'tkdn', 'merek', 'teknis'],
    'prepare-disposition': ['disposisi', 'arahan pimpinan', 'unit tujuan', 'tindak lanjut'],
    'prepare-archive-record': ['arsip', 'retensi', 'metadata arsip', 'temu balik'],
    'explain-policy-for-public': ['bahasa awam', 'faq', 'jelaskan sederhana', 'plain language', 'publik'],
    'summarize-meeting-record': ['notulen', 'rapat', 'keputusan', 'pic', 'action item', 'berita acara'],
    'request-approval-path': ['approval', 'approve', 'otorisasi', 'siapa yang setuju', 'jalur persetujuan'],
    'escalate-blocker': ['eskalasi', 'hold', 'blokir', 'blocked', 'tidak bisa lanjut'],
}

ROLE_KEYWORDS = {
    'top-layer__gov-ai_yayak': ['bantu', 'arahkan', 'klasifikasi', 'langkah', 'proses'],
    'kebijakan-dan-hukum__analis-kebijakan_azis': ['regulasi', 'kebijakan', 'policy brief', 'opsi kebijakan'],
    'kebijakan-dan-hukum__konsultan-hukum_audy': ['kontrak', 'mou', 'pks', 'legal', 'klausul'],
    'kebijakan-dan-hukum__monitor-kepatuhan-hukum_edi': ['audit', 'kepatuhan', 'bukti', 'compliance'],
    'perencanaan-dan-anggaran__perencana-program_faris': ['kak', 'tor', 'renstra', 'indikator', 'program'],
    'perencanaan-dan-anggaran__analis-anggaran_anastasia': ['rab', 'anggaran', 'sbm', 'pagu', 'biaya'],
    'perencanaan-dan-anggaran__monitor-kepatuhan-anggaran_nanang': ['audit anggaran', 'sbm check', 'kepatuhan anggaran'],
    'pengadaan-barang-dan-jasa__admin-pengadaan_ihsan': ['sirup', 'lkpp', 'tender', 'paket pengadaan'],
    'pengadaan-barang-dan-jasa__evaluator-vendor_dendy': ['vendor', 'penyedia', 'kualifikasi', 'shortlist'],
    'pengadaan-barang-dan-jasa__penjaga-spesifikasi_hafidus': ['spesifikasi', 'sni', 'tkdn', 'merek'],
    'data-dan-analitik__koordinator-data_ardy': ['dataset', 'metadata', 'database', 'interoperabilitas'],
    'data-dan-analitik__analisis-statistik_hanan': ['statistik', 'indeks', 'tren', 'outlier', 'regresi'],
    'data-dan-analitik__gis-analyst_varin': ['gis', 'peta', 'spasial', 'layer', 'overlay'],
    'komunikasi-dan-dokumen__penulis-naskah_alfian': ['surat', 'nota dinas', 'memo', 'undangan'],
    'komunikasi-dan-dokumen__notulis_anjungan': ['notulen', 'rapat', 'pic', 'action item'],
    'komunikasi-dan-dokumen__penerjemah-kebijakan_iqbal': ['bahasa awam', 'faq', 'plain language'],
    'sdm-dan-kinerja__asisten-sdm_satria': ['absensi', 'cuti', 'pegawai', 'kepegawaian'],
    'sdm-dan-kinerja__asisten-pelatihan_tabah': ['diklat', 'pelatihan', 'sertifikasi', 'kompetensi'],
    'sdm-dan-kinerja__monitor-kinerja_reza': ['iku', 'sakip', 'kinerja', 'capaian', 'dashboard'],
    'hubungan-eksternal-dan-lapangan__liaison-publik_marlin': ['pengaduan', 'wbs', 'masyarakat', 'stakeholder'],
    'hubungan-eksternal-dan-lapangan__koordinator-lapangan_syarah': ['lapangan', 'sitrep', 'desa', 'progres'],
    'hubungan-eksternal-dan-lapangan__manajemen-risiko_sauria': ['risiko', 'mitigasi', 'risk register'],
    'tata-usaha__admin-persuratan_harrisal': ['surat masuk', 'surat keluar', 'nomor surat'],
    'tata-usaha__asisten-disposisi_woro': ['disposisi', 'tindak lanjut'],
    'tata-usaha__arsiparis-digital_sovia': ['arsip', 'retensi', 'dokumen final'],
    'tata-usaha__agenda-dan-protokol_ikhsan': ['agenda', 'jadwal', 'protokol'],
    'tata-usaha__admin-layanan-internal_ika': ['atk', 'fasilitas', 'kendaraan dinas', 'layanan internal'],
    'tata-usaha__monitor-sla-tata-usaha_izza': ['sla', 'backlog', 'keterlambatan'],
    'bottom-gate__bot-eskalasi_winda': ['eskalasi', 'hold', 'blokir', 'otorisasi'],
}

ACTION_LEVEL_HINTS = {
    'L4': ['kirim resmi', 'tandatangani', 'publish', 'eksekusi', 'approve sekarang', 'ubah status final'],
    'L3': ['draft surat', 'legal memo', 'evaluasi vendor', 'rekomendasi anggaran', 'disposisi'],
    'L2': ['rekomendasi', 'analisis', 'cek', 'review', 'validasi'],
    'L1': ['ringkas', 'outline', 'daftar dokumen', 'catatan awal'],
    'L0': ['cari', 'route', 'klasifikasi', 'lihat status'],
}

SENSITIVE_HINTS = ['restricted', 'sensitive', 'rahasia', 'pegawai', 'kontrak', 'anggaran', 'pengaduan', 'wbs']
IMPACT_HINTS = ['legal', 'fiscal', 'procurement', 'personnel', 'public', 'reputational', 'hukum', 'anggaran', 'pengadaan', 'pegawai', 'publik']


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', text.lower()).strip()


def detect_intent(text: str) -> str:
    scores: dict[str, int] = {}
    for intent, keywords in INTENT_RULES.items():
        scores[intent] = sum(2 if kw in text else 0 for kw in keywords)
    best = max(scores.items(), key=lambda item: item[1])
    return best[0] if best[1] > 0 else 'route-intake'


def detect_role(text: str) -> str:
    scores: dict[str, int] = {}
    for role, keywords in ROLE_KEYWORDS.items():
        scores[role] = sum(2 if kw in text else 0 for kw in keywords)
    best = max(scores.items(), key=lambda item: item[1])
    return best[0] if best[1] > 0 else 'top-layer__gov-ai_yayak'


def detect_action_level(text: str) -> str:
    for level in ['L4', 'L3', 'L2', 'L1', 'L0']:
        if any(kw in text for kw in ACTION_LEVEL_HINTS[level]):
            return level
    return 'L2'


def infer_work_state(intent: str, action_level: str, evidence_complete: bool, approval_owner_known: bool) -> tuple[str, str]:
    if intent == 'route-intake':
        return 'classified', 'draft'
    if not evidence_complete:
        return 'intake-check', 'draft'
    if intent in {'review-compliance', 'review-legal-risk', 'review-budget-fit', 'review-specification-neutrality'}:
        return 'reviewing', 'review'
    if intent in {'prepare-archive-record'}:
        return 'reviewing', 'review'
    if action_level in {'L3', 'L4'} and approval_owner_known:
        return 'awaiting-approval', 'review'
    if action_level in {'L3', 'L4'} and not approval_owner_known:
        return 'blocked', 'hold'
    return 'drafting', 'draft'


def build_trace_id(text: str) -> str:
    return 'trace-' + hashlib.sha1(text.encode()).hexdigest()[:12]


def build_required_evidence(intent: str, role_slug: str) -> list[str]:
    baseline = ['task objective', 'source provenance']
    if intent in {'draft-formal-artifact', 'prepare-disposition', 'prepare-archive-record'}:
        baseline += ['document basis', 'approval owner']
    if 'anggaran' in role_slug or intent == 'review-budget-fit':
        baseline += ['budget basis', 'standard or pagu reference']
    if 'hukum' in role_slug or intent == 'review-legal-risk':
        baseline += ['governing text', 'authority basis']
    if 'pengadaan' in role_slug or intent == 'review-specification-neutrality':
        baseline += ['package evidence', 'review criteria']
    return baseline


def next_role_for(role_slug: str, intent: str, authority_matrix: dict[str, Any]) -> str | None:
    role_entry = next((r for r in authority_matrix['roles'] if r['role_slug'] == role_slug), None)
    if role_entry:
        return role_entry.get('default_next_handoff')
    if intent == 'escalate-blocker':
        return 'bottom-gate__bot-eskalasi_winda'
    return None


def gate_decision(action_level: str, evidence_complete: bool, approval_owner_known: bool, has_material_impact: bool, current_role_class: str) -> tuple[str, str | None, str | None]:
    if not evidence_complete:
        return 'HOLD', None, 'missing evidence basis'
    if action_level == 'L4' and not approval_owner_known:
        return 'ESCALATE_TO', 'bottom-gate__bot-eskalasi_winda', 'approval owner unclear for L4'
    if action_level in {'L3', 'L4'} and has_material_impact:
        return 'REVIEW_NEEDED', None, 'human approval required for consequential action'
    if current_role_class == 'monitor' and has_material_impact:
        return 'REVIEW_NEEDED', None, 'monitor finding should be acknowledged by human owner'
    return 'PROCEED', None, None


def build_decision(payload: dict[str, Any]) -> dict[str, Any]:
    rules = load_json(CONFIGS / 'government_logic_rules.json')
    authority_matrix = load_json(CONFIGS / 'authority_matrix.json')
    text = normalize(payload.get('request_text', ''))
    role_slug = payload.get('current_role_slug') or detect_role(text)
    role_entry = next((r for r in authority_matrix['roles'] if r['role_slug'] == role_slug), None)
    role_class = role_entry['role_class'] if role_entry else 'specialist'
    intent = payload.get('intent_class') or detect_intent(text)
    action_level = payload.get('action_level') or detect_action_level(text)
    evidence_complete = bool(payload.get('evidence_complete', False))
    approval_owner_known = bool(payload.get('approval_owner_known', False))
    has_material_impact = bool(payload.get('material_impact', any(h in text for h in IMPACT_HINTS)))
    sensitive = bool(payload.get('sensitive', any(h in text for h in SENSITIVE_HINTS)))
    work_state, document_status = infer_work_state(intent, action_level, evidence_complete, approval_owner_known)
    next_owner = payload.get('next_owner_role') or next_role_for(role_slug, intent, authority_matrix)
    required_evidence = payload.get('required_evidence') or build_required_evidence(intent, role_slug)
    approval_gate = None if action_level in {'L0', 'L1'} else (role_entry.get('approval_owner_hint') if role_entry else 'human accountable owner')
    stop_condition = None
    decision, escalate_to, reason = gate_decision(action_level, evidence_complete, approval_owner_known, has_material_impact or sensitive, role_class)
    if decision == 'HOLD':
        work_state = 'blocked'
        document_status = 'hold'
        stop_condition = reason
    elif decision == 'ESCALATE_TO':
        work_state = 'escalated'
        document_status = 'hold'
        stop_condition = reason
        next_owner = escalate_to
    elif decision == 'REVIEW_NEEDED' and work_state not in {'awaiting-approval', 'reviewing'}:
        work_state = 'awaiting-approval'
        document_status = 'review'
        stop_condition = reason

    trace_id = payload.get('trace_id') or build_trace_id(text)
    output = {
        'trace_id': trace_id,
        'intent_class': intent,
        'work_state': work_state,
        'current_owner_role': role_slug,
        'next_owner_role': next_owner,
        'action_level': action_level,
        'document_status': document_status,
        'required_evidence': required_evidence,
        'approval_gate': approval_gate,
        'stop_condition': stop_condition,
        'human_touchpoint_required': action_level in {'L3', 'L4'} or has_material_impact or sensitive,
        'notes': payload.get('notes', ''),
        'decision_gate': decision,
        'decision_reason': reason,
        'government_logic_version': rules['version'],
    }
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description='Draft government decision engine for Gov-Agentic AI.')
    parser.add_argument('--input-json', help='Path to input JSON payload')
    parser.add_argument('--request-text', help='Raw request text if not using --input-json')
    parser.add_argument('--current-role-slug', help='Optional current role slug')
    parser.add_argument('--evidence-complete', action='store_true', help='Mark evidence as complete')
    parser.add_argument('--approval-owner-known', action='store_true', help='Mark approval owner as known')
    parser.add_argument('--material-impact', action='store_true', help='Mark the request as materially impactful')
    parser.add_argument('--sensitive', action='store_true', help='Mark the request as sensitive')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON')
    args = parser.parse_args()

    if args.input_json:
        payload = load_json(Path(args.input_json))
    else:
        payload = {
            'request_text': args.request_text or '',
            'current_role_slug': args.current_role_slug,
            'evidence_complete': args.evidence_complete,
            'approval_owner_known': args.approval_owner_known,
            'material_impact': args.material_impact,
            'sensitive': args.sensitive,
        }
    if not payload.get('request_text'):
        print('ERROR: request_text is required', file=sys.stderr)
        return 2
    decision = build_decision(payload)
    print(json.dumps(decision, indent=2 if args.pretty else None, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
