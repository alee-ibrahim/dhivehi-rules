# Radheef lexicon — provenance

- **Source:** ދިވެހިބަހުގެ ރަދީފު (Radheef), the official dictionary of the Dhivehi
  language, Dhivehi Academy, Republic of Maldives.
- **Extracted from:** Radheef Android app v2.1.6 (`Radheef_2.1.6.apk`), bundled
  asset `assets/databases/radheefdv` — a plain (unencrypted) SQLite 3 database,
  table `radheef(_id, headword, wordclass, definition)`.
- **Extracted on:** 2026-09-26.
- **Entries:** 38,778 (38,719 unique headwords). Definitions are Dhivehi prose,
  originally `<ul><li>`-marked per sense; markup stripped, senses split into a list.

## Files
- `radheef.jsonl`             — one entry per line: {id, headword, wordclass, senses[]}
- `radheef_headwords.txt`     — sorted unique headwords
- `corpus_vocab.tsv`          — corpus-attested word forms (count>=5)
- `wordclass_labels.json`     — POS code map (some codes unverified)
- `../rules/dba_thikijehi_rules.json` — DBA 2024 rules for dotted (thikijehi) letters

Arabic-derived letters can be folded to their plain twin as a lookup fallback,
following the DBA substitution table (ޚ ޣ ޝ kept), so formal spellings still match.
