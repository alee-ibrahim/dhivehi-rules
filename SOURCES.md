# Sources and provenance

## Authoritative sources

| Source | Details | Used in |
|---|---|---|
| DBA thikijehi rules, 2024 | ތާނައިގައި ހުރި ނުކުތާޖެހި އަކުރުތައް ބޭނުންކުރާނެ ހަމަ (rules for using dotted letters in Thaana), Dhivehi Bahuge Academy, ISBN 978-99915-69-61-1, 14 April 2024 | `rules/dba_thikijehi_rules.json`, `dhivehi_rules/dba_rules.py`, `dhivehi_rules/dba_fix.py`, `guides/orthography.md` |
| DBA word division, 2024 | ލަފުޒު ވަކިކޮށް ލިޔުމުގެ ގަވާއިދު, Dhivehi Bahuge Academy, 2024. Supersedes the 2013 edition (ލަފުޒު ވަކިކުރުން, 2013), which is no longer followed where they differ | `dhivehi_rules/dba_rules.py` (rule ids cite its sections), `dhivehi_rules/dba_fix.py` |
| DBA Latin romanisation, 1977 | ދިވެހިބަސް އިނގިރޭސި (ލެޓިން) އަކުރުން ލިޔުމުގެ ޤަވާޢިދު, official rules of 23 May 1977 | `dhivehi_rules/thaana_latin.py` (68 booklet examples in `BOOK_EXAMPLES`) |
| Gazette iulaan/4791, 2013 | Dhivehi Academy announcement of the correct forms of the Hijri and Gregorian month names, Government Gazette, 13 August 2013, https://www.gazette.gov.mv/iulaan/4791 | `rules/calendar.json` |
| Radheef | ދިވެހިބަހުގެ ރަދީފު, the Dhivehi Academy's dictionary, extracted from the DBA Radheef app (v2.1.6); 38,778 entries, 38,719 unique headwords. Details in `lexicon/PROVENANCE.md` | `lexicon/radheef.jsonl`, `lexicon/radheef_headwords.txt`, `lexicon/radheef_labels.json`, `lexicon/wordclass_labels.json` |
| Corpus counts | Word-form counts (count >= 5, about 506k forms) from crawled Dhivehi news sites, public speeches and People's Majlis sitting records | `lexicon/corpus_vocab.tsv`; the evidence counts in `rules/grammar_rules.json`, `rules/register_rules.json`, `rules/numbers.json`, `rules/calendar.json`, `guides/grammar.md`, `guides/spoken_register.md` |

## Per file

| File | Origin |
|---|---|
| `rules/dba_thikijehi_rules.json` | extracted from the DBA 2024 thikijehi book; homograph list curated from Radheef pairs whose definitions differ |
| `rules/grammar_rules.json` | corpus-mined grammar rules (news, speeches, Majlis sittings), 2026-10-15 |
| `rules/register_rules.json` | corpus-mined register rules for audience-facing speech |
| `rules/protected_names.json` | personal names found by position (after a title, on a speaker line) in the corpus |
| `rules/calendar.json` | month names from Gazette iulaan/4791; weekday names and date formats as used in official letters; non-standard month variants seen in use; corpus and Radheef evidence added from `lexicon/` |
| `rules/numbers.json` | Dhivehi number words as spelled out for TTS; forms checked against corpus counts |
| `rules/pronunciation.json` | TTS reading rules: atoll codes, fixed substitutions, spoken-register endings and a respelling list |
| `lexicon/*` | Radheef extraction and corpus vocabulary counts; see `lexicon/PROVENANCE.md` |
| `guides/grammar.md`, `guides/spoken_register.md` | written from the corpus mining behind `grammar_rules.json` and `register_rules.json` |
| `guides/orthography.md` | written for this repository from the DBA orthography decisions and verification practice |
| `dhivehi_rules/*.py` | implementations of the DBA rules above (`thaana.py`, `dba_rules.py`, `dba_fix.py`, `script_gate.py`, `thaana_latin.py`) |

## Not included

The DBA book PDFs and their text extractions, audit worksheets, earlier lexicon files and
evaluation sets are deliberately left out.
