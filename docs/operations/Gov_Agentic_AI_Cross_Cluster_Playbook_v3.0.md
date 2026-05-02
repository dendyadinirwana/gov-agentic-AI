# Gov Agentic AI Cross-Cluster Playbook v3.0

Playbook ini dibuat sebagai "buku skenario operasional" untuk Yayak dan seluruh agent. Fokusnya bukan hanya siapa dipanggil, tetapi bagaimana alur kerja bergerak, kapan berhenti, siapa memegang keputusan, dan bagaimana memulihkan failure.

## 1. Universal Mission Loop
1. **Sense** - Yayak membaca intent, trigger keyword, data class, dan risiko awal.
2. **Route** - Yayak memilih specialist agent dan membuat `trace_id`.
3. **Ground** - Agent mengambil rujukan dari memory/knowledge layer yang benar.
4. **Draft / Analyze** - Agent menghasilkan output minimum SOP-AI.
5. **Challenge** - Monitor/Kepatuhan atau role reviewer menantang asumsi, bukti, dan boundary.
6. **Resolve** - Conflict matrix menentukan tie-breaker.
7. **Human Gate** - HITL reviewer memberi approve, reject, revise, delegate, atau hold.
8. **Archive** - Output, sumber, keputusan, dan feedback masuk audit log.

## 2. Creative Scenario Patterns

### Pattern A - Surat Kilat Pimpinan
- Trigger: "buat surat undangan koordinasi besok pagi".
- Route: Yayak -> Harrisal -> Alfian -> Woro -> Winda jika eksternal.
- Memory: mem9 recall preferensi unit; RAG ambil template undangan aktif; DB cek nomor surat terakhir.
- Human Gate: Kasubbag TU + pejabat penandatangan.
- Failure Recovery: jika nomor surat belum tersedia, Harrisal hold draft dan minta validasi TU.

### Pattern B - Kebijakan Baru Butuh Anggaran
- Trigger: "buat policy brief dan estimasi biaya program baru".
- Route: Yayak -> Azis -> Audy -> Faris -> Anastasia -> Nanang.
- Conflict Likely: Azis bilang opsi layak, Anastasia bilang pagu tidak cukup.
- Tie-breaker: Anastasia/Nanang menang untuk feasibility fiskal.
- Human Gate: Kasubdit + KPA.

### Pattern C - Pengadaan dengan Spek Rawan Bias
- Trigger: "buat spek laptop untuk pengadaan e-Katalog".
- Route: Yayak -> Ihsan -> Hafidus -> Dendy -> Winda.
- Red Flag: Hafidus mendeteksi spek mengunci merek tertentu.
- Resolution: Hafidus menang, paket hold.
- Human Gate: PPK/Pokja review spek netral.

### Pattern D - Data Desa Konflik
- Trigger: "buat analisis IDM kecamatan X".
- Route: Yayak -> Ardy -> Hanan -> Varin.
- Conflict: Ardy punya dataset, Hanan menemukan outlier dan metadata tidak lengkap.
- Tie-breaker: Hanan menang untuk validitas metode.
- Human Gate: Walidata validasi dataset sebelum rekomendasi final.

### Pattern E - WBS / Pengaduan Sensitif
- Trigger: "ada laporan dugaan penyimpangan".
- Route: Yayak -> Marlin -> Sauria -> Winda.
- Memory Rule: jangan simpan identitas pelapor ke mem9; simpan ke operational DB restricted.
- Human Gate: Inspektorat / ULT.
- Failure Recovery: jika data tidak cukup, status HOLD confidential dan minta bukti tambahan.

### Pattern F - Disposisi Terlambat
- Trigger: "surat ini belum ditindaklanjuti 5 hari".
- Route: Yayak -> Harrisal -> Woro -> Izza -> Winda.
- Conflict: Harrisal menganggap surat rutin, Izza menandai SLA merah.
- Tie-breaker: Izza menang untuk SLA.
- Human Gate: Sekretaris Pimpinan menetapkan unit dan tenggat baru.

## 3. Conflict Matrix
- Azis vs Edi: Edi menang untuk kepatuhan; route ke Kabag Kebijakan + Biro Hukum.
- Faris vs Anastasia: Anastasia menang untuk feasibility fiskal; route ke Kasubdit + KPA.
- Anastasia vs Nanang: Nanang menang untuk SBM/account compliance; route ke KPA/APIP.
- Ihsan vs Hafidus: Hafidus menang untuk netralitas spesifikasi; route ke PPK/Pokja.
- Dendy vs Monitor Kepatuhan Pengadaan: kepatuhan menang untuk vendor red flag; route ke Pokja + Inspektorat.
- Ardy vs Hanan: Hanan menang untuk validitas metode; route ke Walidata.
- Marlin vs Sauria: Sauria menang untuk risiko reputasi/sensitif; route ke Humas/Inspektorat.
- Harrisal vs Woro: Woro menang untuk urgency routing disposisi.
- Yayak vs Specialist: specialist boleh koreksi routing satu kali; bila unresolved, Winda menentukan path.

## 4. Failure Recovery Cards
- **Incomplete Evidence**: turunkan ke retrieval-only, tampilkan missing source, minta klarifikasi.
- **Sensitive Data Detected**: redaction, access check, stop public output.
- **SLA Breach**: Izza/Selia-style monitor membuat status merah, Winda notifikasi pejabat.
- **Conflicting Sources**: jangan sintesis paksa; tampilkan konflik; eskalasi sesuai tie-breaker.
- **Human No Response**: reminder 1x, lalu HOLD dan catat pending approval.

## 5. Output Contract
Setiap scenario output wajib punya: `trace_id`, ringkasan, evidence map, assumption log, confidence, red flag, human touchpoint, next step, dan audit status.
