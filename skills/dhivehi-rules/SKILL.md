---
name: dhivehi-rules
description: Write, check, fix and romanise Dhivehi (Thaana) text to the Dhivehi Academy standard. Use whenever an agent writes or edits Dhivehi, prepares Dhivehi for TTS or publication, spell-checks or proofreads Thaana, converts Dhivehi to Latin script, or needs official month names, number words or dotted-letter (thikijehi) rules.
---

# Dhivehi rules

This repository holds the Dhivehi Academy (DBA) standards as data (`rules/`), the Radheef
dictionary and corpus vocabulary (`lexicon/`), guides (`guides/`) and a dependency-free
Python checker (`dhivehi_rules/`). Use the checker; don't rely on memory for Dhivehi
spelling, word division or register.

## Setup

```
git clone https://github.com/alee-ibrahim/dhivehi-rules
pip install -e dhivehi-rules        # editable install is required: data is read from the checkout
```

## Workflow for any Dhivehi you write

1. **Write it as a native speaker would.** No invented words, no word-for-word calques of
   English. Loanwords are written as they are said. If unsure a word exists, look it up in
   `lexicon/radheef_headwords.txt` or `lexicon/corpus_vocab.tsv`.
2. **Apply safe fixes:** `python -m dhivehi_rules.dba_fix "<text>"`. Only audited, safe
   corrections are applied, and each change is listed.
3. **Check:** `python -m dhivehi_rules.dba_rules --grammar "<text>"`, adding
   `--context ad|presenter|video` for text addressed to an audience.
4. **Gate before TTS or publishing:**
   `python -m dhivehi_rules.script_gate --context video "<text>"` (or `--file lines.json`).
   Exit 0 means clean or warnings only, 2 means errors. Fix every error and run it again.
   Don't use `--force` unless a person tells you to.
5. **Warnings** (rule ids starting with `~`) need human judgement. Report them; don't
   silently "fix" them.

From Python:

```python
from dhivehi_rules import thaana, dba_rules, dba_fix, thaana_latin
from dhivehi_rules.script_gate import check_script
text = thaana.normalise(text)
fixed, changes = dba_fix.fix(text)
ok, report = check_script(fixed, "video")
latin = thaana_latin.romanise(fixed)      # official 1977 romanisation
```

## Rules to keep in mind while writing

- **Dotted letters: plain by default.** ޘ→ސ, ޛ ޟ ޡ ޜ→ޒ, ޥ→ވ always. In ordinary words
  ޙ→ހ, ޞ→ސ, ޠ→ތ, ޢ→އ, ޤ→ގ (ގައުމު, އުސޫލު, ހަގީގަތް). Never drop ޚ ޣ ޝ (ޚަބަރު).
  Keep dots for homographs (ޢަމަލު deed vs އަމަލު), Hijri months, Arabic personal names
  and titles, and religious terms; write Allah with the ligature ﷲ.
- **Word division (2024).** Ordinals join: 2021ވަނަ. These particles stand apart: ވެސް,
  ނަމަވެސް, ފަދަ, ޓަކައި, ފިޔަވައި, މެނުވީ, ކަހަލަ. Plural and question particles join: ދޮރުތައް.
  No space before a full stop and one space after it.
- **Grammar.** Use the right existential verb: ސުވާލެއް **އޮތް** ނަމަ, not ހުރި.
  Honorific verbs are never used for yourself. No plural noun after a numeral.
- **Register for an audience.** "You" is ތިޔަބޭފުޅުން, never ކަލޭ or ތިބާ. "I/we" is
  އަޅުގަނޑު / އަޅުގަނޑުމެން, not އަހަރެން. Ask politely: ގުޅުއްވާ.
- **Speech.** Spoken Dhivehi drops the written -ެވެ sentence endings. See
  `rules/pronunciation.json` for spoken forms, atoll codes and respellings.
- **Months and numbers.** Use `rules/calendar.json` (official 2013 forms) and
  `rules/numbers.json` (standalone and pre-noun forms). Don't spell them from memory.
- **Corpus over checker.** When a mechanical check disagrees with clearly common native
  usage in `lexicon/corpus_vocab.tsv`, follow the usage and report the disagreement.

## Where to read more

- `guides/orthography.md`: the full DBA standard, and what may be auto-fixed versus only flagged
- `guides/grammar.md`, `guides/spoken_register.md`: the evidence behind the grammar and register rules
- `SOURCES.md`: the source of every rule
