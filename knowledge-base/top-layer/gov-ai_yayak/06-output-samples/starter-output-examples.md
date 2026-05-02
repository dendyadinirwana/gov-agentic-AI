# Starter Output Examples — GOV-AI (Yayak)

## Example 1 — Surat Routing
- **User request:** "buat surat undangan rapat koordinasi besok"
- **Expected route:** Harrisal for correspondence intake and numbering context, Alfian for draft wording, Woro for disposition/recipient path, then human approver.
- **Good router output:** marks this as L3 formal artifact preparation, lists missing inputs such as recipient, date, and signatory, and names the human approval gate.

## Example 2 — RAB Routing
- **User request:** "cek apakah honor narasumber ini sesuai SBM"
- **Expected route:** Anastasia for budget structure, Nanang for compliance challenge, optionally Faris for program alignment.
- **Good router output:** states fiscal impact, requires evidence such as SBM and pagu context, and keeps confidence low until source basis is attached.

## Example 3 — Legal Risk Routing
- **User request:** "apakah klausul PKS ini aman"
- **Expected route:** Audy for clause review and legal risk analysis, with human legal review mandatory before use.
- **Good router output:** labels legal review as required, names the missing source or clause context, and prevents informal approval language.
