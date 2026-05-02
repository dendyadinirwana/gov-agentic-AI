# Ingestion Guide

## Metadata minimum per dokumen
- `title`
- `role_owner`
- `cluster`
- `document_type`
- `source_unit`
- `effective_date`
- `review_date`
- `classification` : public | internal | restricted | sensitive
- `status` : draft | active | superseded | archived
- `summary`
- `keywords`
- `human_reviewer`

## Checklist sebelum masuk `08-ingestion-ready`
- Sudah dibersihkan dari duplikasi/halaman kosong.
- Versi dokumen jelas dan masih berlaku.
- Metadata `.json` pendamping sudah diisi.
- Dokumen sensitive sudah dimasking bila perlu.
- Reviewer manusia sudah menyetujui dokumen sebagai sumber yang layak.
