# dhivehi-rules

The single source of truth for how Dhivehi is written, checked and read aloud: the
Dhivehi Academy (DBA) standards as machine-readable data, the Radheef lexicon and corpus
vocabulary, human-readable guides, and a small dependency-free Python
package that applies them.

## Layout

```
rules/        machine-readable rules (JSON)
  dba_thikijehi_rules.json   DBA 2024 dotted-letter (thikijehi) rules
  grammar_rules.json         corpus-backed grammar rules (existential agreement, honorifics, plurals...)
  register_rules.json        word choice for audience-facing speech (ad, presenter, video)
  protected_names.json       personal names whose dotted spelling is kept
  calendar.json              Hijri and Gregorian months (official 2013 Gazette forms), weekdays
  numbers.json               number words 0-99 (standalone and pre-noun), hundreds, thousands, scales
  pronunciation.json         written -> spoken rules for TTS (atoll codes, ligatures, -ެވެ endings, respellings)
lexicon/      Radheef dictionary and corpus vocabulary
  radheef.jsonl, radheef_headwords.txt, radheef_labels.json, wordclass_labels.json,
  corpus_vocab.tsv, PROVENANCE.md
guides/       human-readable guides
  orthography.md             the DBA standard as applied here: what to auto-fix, what only to flag
  grammar.md                 evidence behind grammar_rules.json
  spoken_register.md         evidence behind register_rules.json
dhivehi_rules/  Python package (standard library only)
  thaana.py         normalise() and validate(): well-formed Thaana
  dba_rules.py      check(): DBA spelling and word division, plus register and grammar
  dba_fix.py        fix(): the corrections that are safe to apply automatically
  script_gate.py    the gate every Dhivehi script passes before TTS
  thaana_latin.py   romanise(): official 1977 Latin romanisation
SOURCES.md        provenance of every file
skills/dhivehi-rules/SKILL.md   agent skill: how an AI agent should write and check Dhivehi
```

## Install

```
pip install -e path/to/dhivehi-rules
```

Use an editable install. The package reads `rules/` and `lexicon/` from the repository,
located relative to the package directory, so it must run from the checkout.

## Use

The pre-TTS gate. No Dhivehi text goes to TTS without passing it:

```
python -m dhivehi_rules.script_gate --context ad "ސުވާލެއް އޮތް ނަމަ، ގުޅުއްވާ."
python -m dhivehi_rules.script_gate --context video --file vo/lines.json    # JSON {key: line} or [line, ...]
python -m dhivehi_rules.script_gate --context presenter --file script.md   # every Thaana line
```

Exit 0 = clean or warnings only, 2 = errors, 1 = bad usage. Contexts: `ad`, `presenter`,
`video`. `--force` lets errors through, with a banner and a record in `logs/gate_overrides.log`.
The same is installed as the `dhivehi-script-gate` command.

From Python:

```python
from dhivehi_rules.script_gate import check_script, gate, gate_lines
ok, report = check_script(text, "video")          # never raises
gate(text, label="intro", context="ad")           # SystemExit(2) on errors
gate_lines({"h": line1, "c1": line2}, context="ad")

from dhivehi_rules import thaana, dba_rules, dba_fix, thaana_latin
thaana.validate(thaana.normalise(text)).orthography_errors
dba_rules.check(text)                   # DBA spelling and word division only
dba_rules.check(text, "presenter")      # plus register and grammar
fixed, changes = dba_fix.fix(text)      # safe automatic corrections, with a change log
thaana_latin.romanise(text)
```

Command-line checks:

```
python -m dhivehi_rules.dba_rules "އަހަރެންވެސް 14 ވަނަ ދުވަހު ދިޔައީމެވެ ."
python -m dhivehi_rules.dba_rules --grammar "ސުވާލެއް ހުރި ނަމަ"
python -m dhivehi_rules.dba_fix "ޢިއްޒަތްތެރި ރައީސް 2021 ވަނަ އަހަރުވެސް"
python -m dhivehi_rules.thaana_latin --test       # 68/68 booklet examples
```

The JSON files can be read directly from any language; each one carries `_source` /
`_about` fields that cite where it comes from.

## For AI agents

`skills/dhivehi-rules/SKILL.md` is an agent skill (Claude Code / Agent Skills format) that
tells an agent how to write Dhivehi and which checks to run. Copy the `skills/dhivehi-rules`
folder into your agent's skills directory (for Claude Code: `.claude/skills/`).

## Changing a rule

Cite the source (book and section, or corpus counts) in the data and update `SOURCES.md`.

## License

MIT — see [LICENSE](LICENSE).
