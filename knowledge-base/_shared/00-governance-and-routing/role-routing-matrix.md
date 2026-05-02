# Role Routing Matrix

## Core Routing Rules
- Yayak is the default router and action-level gate.
- Specialist roles execute within domain.
- Monitor/compliance roles challenge unsupported or unsafe outputs.
- Winda resolves unresolved conflict, missing approver paths, and blocked execution.

## Role Class Summary
### Router/Orchestrator
- GOV-AI (Yayak) — `top-layer` — router + intent classifier
### Specialist/Executor
- Analis Kebijakan (Azis) — `kebijakan-dan-hukum` — Regulasi, PP, Permen, policy brief
- Konsultan Hukum (Audy) — `kebijakan-dan-hukum` — Kontrak, risiko hukum, legal note
- Perencana Program (Faris) — `perencanaan-dan-anggaran` — KAK, ToR, rencana kerja, Renstra
- Analis Anggaran (Anastasia) — `perencanaan-dan-anggaran` — RAB, DPP, PPN, SBM
- Admin Pengadaan (Ihsan) — `pengadaan-barang-dan-jasa` — e-Katalog, SIRUP, LKPP
- Evaluator Vendor (Dendy) — `pengadaan-barang-dan-jasa` — Kualifikasi, track record vendor
- Penjaga Spesifikasi (Hafidus) — `pengadaan-barang-dan-jasa` — Cek spesifikasi, flagging, SNI, TKDN
- Koordinator Data (Ardy) — `data-dan-analitik` — IDM, Indeks Desa, SIPD, metadata
- Analisis Statistik (Hanan) — `data-dan-analitik` — Klaster, normalisasi, indeks
- GIS Analyst (Varin) — `data-dan-analitik` — Peta tematik, spasial, layer GIS
- Penulis Naskah (Alfian) — `komunikasi-dan-dokumen` — Surat, nota dinas, surat edaran
- Notulis (Anjungan) — `komunikasi-dan-dokumen` — Notulen, action item, PIC
- Penerjemah Kebijakan (Iqbal) — `komunikasi-dan-dokumen` — Bahasa teknis ke awam
- Asisten SDM (Satria) — `sdm-dan-kinerja` — Absensi, cuti, SKP
- Asisten Pelatihan (Tabah) — `sdm-dan-kinerja` — Bimtek, diklat, sertifikasi
- Liaison Publik (Marlin) — `hubungan-eksternal-dan-lapangan` — SP2D, pengaduan, WBS
- Koordinator Lapangan (Syarah) — `hubungan-eksternal-dan-lapangan` — Pendamping, monitoring desa
- Admin Persuratan (Harrisal) — `tata-usaha` — Surat masuk/keluar, nomor surat
- Asisten Disposisi (Woro) — `tata-usaha` — Disposisi, routing unit, tindak lanjut
- Arsiparis Digital (Sovia) — `tata-usaha` — Arsip digital, retensi, versi final
- Agenda & Protokol (Ikhsan) — `tata-usaha` — Agenda pimpinan, undangan, protokol
- Admin Layanan Internal (Ika) — `tata-usaha` — ATK, fasilitas, kendaraan dinas, ruang rapat
### Monitor/Compliance
- Monitor Kepatuhan Hukum (Edi) — `kebijakan-dan-hukum` — Audit trail, BPK-ready, compliance
- Monitor Kepatuhan Anggaran (Nanang) — `perencanaan-dan-anggaran` — Audit trail anggaran, SBM check
- Monitor Kinerja (Reza) — `sdm-dan-kinerja` — IKU, SAKIP, LKJ
- Manajemen Risiko (Sauria) — `hubungan-eksternal-dan-lapangan` — Risiko proyek, mitigasi
- Monitor SLA Tata Usaha (Izza) — `tata-usaha` — SLA surat, SLA disposisi, backlog administrasi
### Escalation/Fallback
- Bot Eskalasi (Winda) — `bottom-gate` — Teruskan ke pejabat berwenang
