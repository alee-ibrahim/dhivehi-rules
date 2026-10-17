# Grammar rules for generated Dhivehi (LLM-typical errors)

`rules/register_rules.json` covers word choice, and `dba_rules.py` covers spelling and word division.
Neither one checks grammar, so a script could pass both and still say *ސުވާލެއް ހުރި ނަމަ* where a
Maldivian says *ސުވާލެއް އޮތް ނަމަ*. `grammar_rules.json` fills that gap. A rule goes in only if the
corpus backs it (`rules/grammar_rules.json`). Each rule records its counts, and every candidate the corpus did not back is
listed below as rejected.

    python -m dhivehi_rules.dba_rules --grammar "<text>"           # grammar, plus spelling
    python -m dhivehi_rules.dba_rules --context ad "<text>"        # a context implies --grammar
    python -m dhivehi_rules.script_gate --context ad "<text>"      # the pre-TTS gate: everything, exit 2 on errors

A call with no context and no `--grammar` behaves exactly as before. This was verified by diffing
`check()` output on 150 speeches and 300 sun.mv articles. The no-context output was byte-identical.
With `--context presenter` it was identical once the new `gr_*` lines were removed.

## Evidence base

The same corpus as `spoken_register.md`: 26 news sites (about 4 GB of text), 469 public
speeches and 92,958 Majlis sittings. The mining scripts (noun/verb pair extraction, table
building and a KWIC concordancer) were one-off tools and are not part of this repository. Everything was mined on 2026-10-15.

## 1. Existential verb agreement (`gr_exist_agreement`)

Dhivehi has three verbs for "there is / is (located)":

- **ހުރި** for standing and physical things and for most plurals (ހުރެ, ހުރީ, ހުންނަ, އެބަހުރި, ހުއްޓެވެ…)
- **އޮތް** for abstract things and things lying down: ފުރުސަތު, ސުވާލު, ހައްލު, ނިޒާމު, ގާނޫނު, ރަށް, ބިން,
  މަގު, ކާރު, ފޯނު (އޮވެ, އޮތީ, އޮންނަ, އެބައޮތް, އޮތެވެ…)
- **ތިބި** for animate plurals: people and groups (ތިބެ, ތިބީ, ތިބޭ, އެބަތިބި, ތިއްބެވެ…)

Number changes the verb. *ސުވާލެއް* takes **އޮތް** (367 to 30), but *ސުވާލުތައް* takes **ހުރި** (158 to 29;
130 to 15 in a relative clause). *ފުރުސަތު* takes **އޮތް** (10,978 to 26), but *ފުރުސަތުތައް* takes
**ހުރި** (8,455 to 205). So the table is keyed by noun **and** form (indefinite -އެއް, bare, plural).

**How it was mined.** The miner tokenised every document and found each existential verb. It
recorded (a) the word right before the verb (the subject of a predicate, as in 'ސުވާލެއް ހުރި'), unless
that word is a locative, genitive, dative or other oblique, and (b) for a bare participle, the word
right after it (a relative clause, as in 'ހުރި ސުވާލެއް'). That gives 28k noun/verb pairs. The table
keeps the nouns an LLM is likely to use: 79 nouns, plus 25 human plurals from a second pass. The main
pass skipped every word in -ން, because most are ablatives, so it missed the human plurals.

**When it fires.** The corpus must prefer one verb for that noun, form and position with at least 80%
of at least 30 uses (50 for human plurals), and the verb used must have at most 10% (5% for human
plurals). It is an error at 90% or more over 100 or more uses; otherwise a warning. The suggestion
swaps the verb and keeps the ending (ހުރިނަމަ becomes އޮތްނަމަ, އެބަހުރި becomes އެބައޮތް, ހުރީ becomes
ތިބީ).

**Precision guards**, added after reading the hits on 1.36M words of human-written text:

- A relative participle ('ހުރި X') is checked only when nothing before it can be its own subject. In
  'ކެޕޭސިޓީ ހުރި ރަށެއް' ('an island with capacity'), ހުރި agrees with ކެޕޭސިޓީ, not with ރަށެއް.
- A participle followed by a content word ('މަސްވެރިން ހުރި ކަންބޮޑުވުންތައް', 'the concerns fishermen
  have') may agree with that next noun. If the next noun is in the table and accepts the verb, the
  hit is dropped. Otherwise it is only a warning.
- Human plurals are only flagged with ހުރި. 'ރައްޔިތުން އޮތީ ނޫނެކޭ ބުނެފަ' is the stative focus construction.
- Infinitives and verbal nouns in -ން (ހުންނަން, ތިއްބަވަން) are not checked, because they are mostly purposive.

After these guards the rule fires 9 times in 1.36M words of native news, speech and Majlis text
(0.007 per 1,000 words). Most of those are variation that the corpus itself calls rare.

### The table (ހުރި / އޮތް / ތިބި counts)

Only the noun and form slices that met the 80% bar are shown. All counts, including slices that did
not meet it, are in `grammar_rules.json` under `existential.nouns` and `human_plural.nouns`.
"-ތައް" means plural, which includes human plurals in -ން.

| Noun | Form | Takes | Before the verb (ހުރި / އޮތް / ތިބި) | After the participle |
|---|---|---|---|---|
| ސުވާލު | -އެއް | **އޮތް** | 30 / 367 / 0 | – |
| ސުވާލު | bare | **އޮތް** | – | 40 / 228 / 0 |
| ސުވާލު | -ތައް | **ހުރި** | 158 / 29 / 0 | 130 / 15 / 0 |
| ފުރުސަތު | -އެއް | **އޮތް** | 0 / 517 / 0 | 12 / 290 / 0 |
| ފުރުސަތު | bare | **އޮތް** | 26 / 10,978 / 0 | 34 / 661 / 0 |
| ފުރުސަތު | -ތައް | **ހުރި** | – | 8,455 / 205 / 0 |
| މައްސަލަ | -ތައް | **ހުރި** | 3,432 / 360 / 0 | 3,326 / 152 / 11 |
| މަޢުލޫމާތު | bare | **ހުރި** | 228 / 31 / 0 | – |
| މަޢުލޫމާތު | -ތައް | **ހުރި** | 62 / 3 / 0 | 99 / 0 / 0 |
| މައުލޫމާތު | bare | **ހުރި** | 543 / 43 / 0 | 479 / 29 / 7 |
| މައުލޫމާތު | -ތައް | **ހުރި** | 95 / 7 / 0 | 258 / 4 / 0 |
| ވަގުތު | -އެއް | **އޮތް** | 0 / 97 / 0 | – |
| ހައްލު | -އެއް | **އޮތް** | 0 / 133 / 0 | 10 / 258 / 0 |
| ހައްލު | bare | **އޮތް** | 5 / 116 / 0 | 10 / 137 / 0 |
| ޝަރުތު | -ތައް | **ހުރި** | 143 / 33 / 0 | – |
| ޗާންސް | bare | **އޮތް** | 0 / 60 / 0 | – |
| ޖާގަ | -އެއް | **އޮތް** | 45 / 327 / 0 | – |
| ޖާގަ | bare | **އޮތް** | – | 50 / 228 / 0 |
| ޖާގަ | -ތައް | **ހުރި** | – | 51 / 3 / 0 |
| ހައްގު | -އެއް | **އޮތް** | 0 / 136 / 0 | 0 / 236 / 0 |
| ހައްގު | bare | **އޮތް** | 0 / 768 / 0 | 0 / 100 / 0 |
| ހައްގު | -ތައް | **އޮތް** | 19 / 96 / 0 | – |
| ޙައްޤު | -އެއް | **އޮތް** | 0 / 79 / 0 | 3 / 153 / 0 |
| ޙައްޤު | bare | **އޮތް** | 4 / 334 / 0 | 3 / 49 / 0 |
| ނިޒާމު | -އެއް | **އޮތް** | 34 / 932 / 0 | 45 / 250 / 0 |
| ނިޒާމު | bare | **އޮތް** | 102 / 1,319 / 0 | 20 / 238 / 0 |
| ނިޒާމު | -ތައް | **ހުރި** | – | 32 / 6 / 0 |
| ގާނޫނު | -އެއް | **އޮތް** | 7 / 414 / 0 | 14 / 246 / 0 |
| ގާނޫނު | bare | **އޮތް** | 22 / 1,480 / 0 | – |
| ގާނޫނު | -ތައް | **ހުރި** | – | 184 / 16 / 0 |
| ޤާނޫނު | -އެއް | **އޮތް** | 0 / 548 / 0 | 21 / 193 / 0 |
| ޤާނޫނު | bare | **އޮތް** | 9 / 545 / 0 | 26 / 138 / 4 |
| ޤާނޫނު | -ތައް | **ހުރި** | – | 153 / 6 / 0 |
| އުސޫލު | -އެއް | **އޮތް** | 8 / 541 / 0 | 8 / 190 / 0 |
| އުސޫލު | bare | **އޮތް** | 24 / 485 / 0 | 7 / 386 / 3 |
| ބާރު | -އެއް | **އޮތް** | 112 / 627 / 0 | – |
| ބާރު | bare | **އޮތް** | 585 / 3,434 / 4 | – |
| ބާރު | -ތައް | **އޮތް** | 51 / 319 / 28 | – |
| ގުޅުން | bare | **އޮތް** | – | 331 / 9,724 / 0 |
| ގުޅުން | -ތައް | **އޮތް** | 69 / 410 / 0 | 47 / 716 / 0 |
| ބިރު | -އެއް | **އޮތް** | 0 / 76 / 0 | – |
| ބިރު | bare | **އޮތް** | 43 / 2,796 / 0 | – |
| ނުރައްކާ | bare | **އޮތް** | 91 / 2,043 / 0 | 71 / 650 / 0 |
| ހާލަތު | -އެއް | **އޮތް** | 19 / 456 / 0 | 16 / 150 / 15 |
| ހާލަތު | bare | **އޮތް** | – | 183 / 1,063 / 68 |
| ހާލަތު | -ތައް | **ހުރި** | 102 / 22 / 0 | – |
| ފައިދާ | -އެއް | **އޮތް** | – | 8 / 84 / 0 |
| ފައިދާ | bare | **ހުރި** | 4,479 / 221 / 0 | – |
| ފައިދާ | -ތައް | **ހުރި** | 121 / 30 / 0 | 40 / 9 / 0 |
| ތަޖުރިބާ | -އެއް | **ހުރި** | 85 / 11 / 0 | – |
| ތަޖުރިބާ | bare | **ހުރި** | 2,383 / 44 / 25 | – |
| ތަޖުރިބާ | -ތައް | **ހުރި** | 60 / 0 / 0 | – |
| އަގު | bare | **ހުރި** | 2,174 / 70 / 0 | – |
| އަގު | -ތައް | **ހުރި** | 511 / 16 / 0 | 101 / 9 / 0 |
| ފައިސާ | -އެއް | **ހުރި** | – | 162 / 38 / 0 |
| ފައިސާ | bare | **ހުރި** | 2,297 / 152 / 4 | 3,338 / 213 / 9 |
| ފައިސާ | -ތައް | **ހުރި** | 81 / 4 / 0 | 377 / 13 / 0 |
| ދަތި | -ތައް | **ހުރި** | 2,096 / 53 / 0 | 1,170 / 45 / 0 |
| ހުނަރު | -އެއް | **ހުރި** | 96 / 0 / 0 | 45 / 0 / 0 |
| ހުނަރު | bare | **ހުރި** | 625 / 23 / 6 | 65 / 0 / 4 |
| ހުނަރު | -ތައް | **ހުރި** | 103 / 0 / 0 | 67 / 0 / 0 |
| ހިދުމަތް | -ތައް | **ހުރި** | – | 122 / 4 / 4 |
| ޚިދުމަތް | -ތައް | **ހުރި** | – | 145 / 14 / 4 |
| ބާވަތް | -އެއް | **ހުރި** | 87 / 0 / 0 | – |
| ބާވަތް | -ތައް | **ހުރި** | 154 / 0 / 0 | 137 / 5 / 0 |
| ކުލަ | -އެއް | **ހުރި** | 87 / 3 / 0 | – |
| ކުލަ | bare | **ހުރި** | 202 / 17 / 0 | 112 / 22 / 0 |
| ކުލަ | -ތައް | **ހުރި** | 38 / 0 / 0 | 46 / 0 / 0 |
| މުދާ | bare | **ހުރި** | 263 / 9 / 0 | 366 / 43 / 3 |
| މުދާ | -ތައް | **ހުރި** | – | 202 / 0 / 0 |
| އެއްޗެހި | bare | **ހުރި** | 718 / 57 / 8 | 1,869 / 35 / 28 |
| އެއްޗެހި | -ތައް | **ހުރި** | 104 / 6 / 0 | 286 / 6 / 9 |
| ސްޓޮކް | bare | **ހުރި** | 111 / 3 / 0 | 51 / 0 / 0 |
| ސައިޒް | bare | **ހުރި** | 27 / 3 / 0 | – |
| ސިފަ | -އެއް | **ހުރި** | 231 / 24 / 0 | 87 / 9 / 0 |
| ސިފަ | bare | **ހުރި** | 224 / 27 / 0 | 107 / 11 / 9 |
| ސިފަ | -ތައް | **ހުރި** | 832 / 10 / 0 | 77 / 3 / 0 |
| ޝަކުވާ | -އެއް | **އޮތް** | 12 / 397 / 0 | – |
| ޝަކުވާ | -ތައް | **ހުރި** | – | 137 / 13 / 0 |
| ސަބަބު | -އެއް | **އޮތް** | 47 / 1,922 / 0 | – |
| ސަބަބު | -ތައް | **ހުރި** | 1,261 / 247 / 0 | – |
| ޖަވާބު | -އެއް | **އޮތް** | 0 / 59 / 0 | – |
| ނަތީޖާ | -އެއް | **އޮތް** | 0 / 105 / 0 | – |
| ނަތީޖާ | bare | **އޮތް** | 16 / 179 / 0 | – |
| ބަދަލު | -އެއް | **އޮތް** | 8 / 370 / 0 | – |
| ބަދަލު | -ތައް | **ހުރި** | 136 / 23 / 0 | 138 / 9 / 3 |
| ތަފާތު | bare | **ހުރި** | 331 / 67 / 0 | – |
| ތަފާތު | -ތައް | **ހުރި** | 654 / 25 / 0 | 169 / 23 / 0 |
| ފަރަގު | bare | **އޮތް** | – | 138 / 638 / 0 |
| ފަރަގު | -ތައް | **ހުރި** | 88 / 5 / 0 | 68 / 0 / 0 |
| ހިޔާލު | -އެއް | **އޮތް** | 11 / 44 / 0 | – |
| ހިޔާލު | bare | **ހުރި** | 463 / 20 / 0 | – |
| ހިޔާލު | -ތައް | **ހުރި** | 58 / 0 / 0 | – |
| ދައުރު | -އެއް | **އޮތް** | 0 / 841 / 0 | – |
| ދައުރު | bare | **އޮތް** | 0 / 316 / 0 | – |
| ޒިންމާ | -އެއް | **އޮތް** | 0 / 326 / 0 | 0 / 236 / 0 |
| ޒިންމާ | bare | **އޮތް** | 4 / 694 / 0 | 9 / 224 / 3 |
| ގެރެންޓީ | bare | **އޮތް** | 5 / 65 / 0 | – |
| ޕްރޮޑަކްޓް | -ތައް | **ހުރި** | – | 36 / 0 / 0 |
| ޝައުގު | bare | **ހުރި** | 311 / 24 / 0 | – |
| ފޮތް | -އެއް | **އޮތް** | 20 / 105 / 0 | – |
| ފޮތް | -ތައް | **ހުރި** | 135 / 3 / 0 | 247 / 0 / 0 |
| ކާރު | -އެއް | **އޮތް** | 0 / 100 / 0 | – |
| ކާރު | bare | **އޮތް** | 25 / 339 / 0 | – |
| ކާރު | -ތައް | **ހުރި** | – | 31 / 0 / 5 |
| ރަށް | -އެއް | **އޮތް** | 19 / 363 / 0 | 103 / 1,040 / 76 |
| ބިން | -ތައް | **ހުރި** | – | 377 / 47 / 0 |
| މަގު | -އެއް | **އޮތް** | 17 / 246 / 0 | 30 / 188 / 0 |
| ގެ | -އެއް | **ހުރި** | 225 / 21 / 0 | 326 / 33 / 10 |
| ގެ | -ތައް | **ހުރި** | 201 / 0 / 3 | 204 / 0 / 8 |
| ފޯނު | -އެއް | **އޮތް** | 10 / 118 / 0 | 12 / 67 / 0 |
| ފޯނު | bare | **އޮތް** | 57 / 1,024 / 0 | 141 / 2,516 / 0 |
| ފިހާރަ | -އެއް | **ހުރި** | 105 / 0 / 0 | 76 / 0 / 0 |
| ފިހާރަ | bare | **ހުރި** | 927 / 6 / 0 | 154 / 0 / 4 |
| ފިހާރަ | -ތައް | **ހުރި** | 161 / 12 / 0 | 54 / 0 / 0 |
| ލިސްޓު | -އެއް | **އޮތް** | 0 / 106 / 0 | 4 / 67 / 4 |
| ލިސްޓު | bare | **އޮތް** | 8 / 64 / 0 | 8 / 47 / 0 |
| ޕްލޭން | -އެއް | **އޮތް** | 0 / 475 / 0 | 0 / 42 / 0 |
| ޕްލޭން | bare | **އޮތް** | – | 6 / 59 / 0 |
| ނަން | -ތައް | **ހުރި** | – | 60 / 7 / 0 |
| ޕްރޮގްރާމް | -އެއް | **އޮތް** | 4 / 31 / 0 | – |
| ޕްރޮގްރާމް | bare | **އޮތް** | 3 / 116 / 0 | – |
| ޕްރޮގްރާމް | -ތައް | **ހުރި** | – | 35 / 0 / 0 |
| އޮފީސް | bare | **ހުރި** | 821 / 35 / 0 | 97 / 13 / 8 |
| އޮފީސް | -ތައް | **ހުރި** | 195 / 7 / 0 | – |
| މީހުން | -ތައް | **ތިބި** | 3 / 17 / 106 | 2,777 / 829 / 15,764 |
| ކުދިން | -ތައް | **ތިބި** | 0 / 4 / 122 | – |
| ބޭފުޅުން | -ތައް | **ތިބި** | 0 / 0 / 72 | – |
| މެމްބަރުން | bare | **ތިބި** | – | 0 / 13 / 171 |
| މެމްބަރުން | -ތައް | **ތިބި** | 0 / 0 / 56 | – |
| މުވައްޒަފުން | bare | **ތިބި** | – | 44 / 17 / 552 |
| މުވައްޒަފުން | -ތައް | **ތިބި** | 0 / 0 / 38 | 5 / 0 / 35 |
| ފުލުހުން | -ތައް | **ތިބި** | – | 29 / 7 / 399 |
| ރައްޔިތުން | -ތައް | **ތިބި** | 0 / 0 / 89 | – |
| ޒުވާނުން | bare | **ތިބި** | – | 59 / 8 / 323 |
| ޒުވާނުން | -ތައް | **ތިބި** | 0 / 0 / 33 | 10 / 0 / 46 |
| ކުޅުންތެރިން | -ތައް | **ތިބި** | 0 / 0 / 171 | – |
| ފަތުރުވެރިން | bare | **ތިބި** | – | 12 / 4 / 96 |
| އަންހެނުން | -ތައް | **ތިބި** | – | 0 / 0 / 46 |
| ޑޮކްޓަރުން | bare | **ތިބި** | – | 24 / 0 / 110 |
| ބަޔަކު | bare | **ތިބި** | 42 / 60 / 5,032 | 306 / 228 / 3,686 |

| Human plural | ހުރި / އޮތް / ތިބި before the verb |
|---|---|
| ސިފައިން | 5 / 29 / 2,870 |
| ރައްޔިތުން | 17 / 118 / 4,012 |
| މީހުން | 173 / 210 / 12,298 |
| މެމްބަރުން | 5 / 11 / 2,257 |
| ބޭފުޅުން | 28 / 41 / 2,191 |
| ކުދިން | 71 / 35 / 2,661 |
| މުވައްޒަފުން | 3 / 6 / 1,554 |
| ދަރިން | 33 / 8 / 1,095 |
| ޓީޗަރުން | 3 / 1 / 216 |
| ފުލުހުން | 16 / 77 / 764 |
| ފިރިހެނުން | 4 / 5 / 221 |
| ފަރާތްތައް | 21 / 18 / 273 |
| ދަރިވަރުން | 1 / 2 / 491 |
| މަސްވެރިން | 3 / 2 / 258 |
| ކުޅުންތެރިން | 14 / 3 / 1,129 |
| އަންހެނުން | 95 / 45 / 368 |
| މުދައްރިސުން | 3 / 0 / 69 |
| ޑޮކްޓަރުން | 3 / 27 / 334 |
| ޒުވާނުން | 3 / 4 / 422 |
| ކަސްޓަމަރުން | 4 / 1 / 105 |
| އެކުވެރިން | 6 / 0 / 204 |
| ވިޔަފާރިވެރިން | 3 / 4 / 140 |
| ބަލިމީހުން | 0 / 1 / 72 |
| ފަތުރުވެރިން | 1 / 2 / 191 |
| ބޭބޭފުޅުން | 0 / 2 / 59 |

**Where the evidence contradicted the expected answer.** މަޢުލޫމާތު was expected to take އޮތް. The
corpus says **ހުރި**: 228 to 31 bare, and 543 to 43 for މައުލޫމާތު. It behaves like a plural mass
noun, so 'މަޢުލޫމާތު ހުރި' is correct and is not flagged. Likewise ތަޖުރިބާ (2,383 to 44), ހުނަރު,
ފައިދާ, އަގު, ފައިސާ, ކުލަ, ބާވަތް, ސިފަ, ހިޔާލު, ފިހާރަ and ގެއެއް all take ހުރި.

## 2. Honorific verb with a first-person ending (`gr_honorific_first_person`, error)

-ނަން means "I/we will". Honorific verbs are for the person addressed or spoken about, and a speaker
lowers their own verb: *އަޅުގަނޑުމެން ޑެލިވަރީ ކޮށްދޭނަން*, not *ކޮށްދެއްވާނަން*.

| Form | Count | Plain form | Count |
|---|---:|---|---:|
| …ކުރައްވާނަން | 43 | …ކުރާނަން | 57,238 |
| …ދެއްވާނަން | 136 (mostly one repeated headline quote) | …ދޭނަން | 20,152 |
| ބައްލަވާ/ގުޅުއްވާ/ހޯއްދަވާ/ދައްކަވާ/ވިދާޅުވާ/ވަޑައިގަންނަވާ + ނަން | 9 | ބަލާ/ގުޅާ/ހޯދާ/ދައްކާ/ދަންނަވާ/ދާ/އަންނާ + ނަން | 11,614 |

Humble forms such as ދަންނަވާނަން and އަރުވާނަން are correct and are not matched.

## 3. Plural after a numeral (`gr_numeral_plural`, error)

After a numeral the noun stays singular: *ދެ ކުލަ*, *ތިން ބާވަތް*. The corpus has 289 numeral words
(ދެ…ދިހަ) followed by a -ތައް/-ތަކެއް noun, against 1,022,764 numeral + word (0.03%). The exception
is ކަންތައް ('matters'), which is lexicalised: 'ދެ ކަންތައް' occurs 1,454 times, so it is exempt.
Digits are not checked, because '2020 މެޗްތައް' is a year.

## 4. Plural on uncountable nouns (`gr_plural_uncountable`, error)

- Abstract -ތެރިކަން nouns: *ބޭނުންތެރިކަންތައް* ('benefits', an English calque) has 0 real uses, against
  118,748 -ތެރިކަން tokens. The 10 regex hits were all the question particle ތަ؟.
- ލޯބި (12,383 / 0 plural), ޝުކުރު (20,555 / 0), ހޫނު (8,779 / 0), ހިލޭ (23,992 / 0), ކޮލިޓީ (3,169 / 22).

## 5. ނަމަ and ނަމަވެސް

- `gr_sentence_initial_nama` (error): "However," at the start of a sentence is **ނަމަވެސް،** (34,553).
  A bare sentence-initial **ނަމަ،** occurs 9 times. ނަމަ means "if" and closes a clause:
  'ސުވާލެއް އޮތް ނަމަ، …'.
- `gr_nama_after_finite` (error): ނަމަ never follows the sentence-final -އެވެ form. The corpus has 1
  such case, against 139,675 word + ނަމަ.

## Rejected candidates (no rule: the evidence was too weak or went the other way)

| Candidate | Evidence | Why rejected |
|---|---|---|
| ގޮތެއް + ހުރި/އޮތް | -އެއް: އޮތް 1,986 / ހުރި 1,341 | Both are common |
| މައްސަލައެއް + ހުރި/އޮތް | singular: އޮތް 1,533 / ހުރި 1,115 | Both are common. The plural takes ހުރި (3,432 / 360) and is in the table |
| ވަގުތު (bare) | ހުރި 1,075 / އޮތް 1,975 / ތިބި 839 | 'މި ވަގުތު' is an adverb. Only ވަގުތެއް → އޮތް (97 / 0) is kept |
| ޝަރުތެއް → އޮތް | 38 / 11 (78%) | Below the 80% bar |
| އޮފަރު → އޮތް | 5 uses | Too few |
| މަޢުލޫމާތު → އޮތް | The corpus says ހުރި, 228 / 31 | The expected rule is wrong, see above |
| human plural + އޮތް | e.g. މީހުން 210 / 12,298 | Focus construction ('ރައްޔިތުން އޮތީ … ބުނެފަ'); only ހުރި is flagged |
| ކުރައްވާ vs ކޮށްދެއްވާ as a request | sentence-final: 7,474 vs 777 | Both are correct polite imperatives ('do' / 'do for us') |
| ތިޔަބޭފުޅުން + plain verb (ކުރާ, ކުރަނީ…) | 2–9, vs 15–17 with the honorific | Too few to say anything |
| "Thanks for watching/your time" calques (ބަލާލުމަށް ޝުކުރިއްޔާ, ތިޔަބޭފުޅުންގެ ވަގުތަށް ޝުކުރިއްޔާ) | 0 hits each, but the native ބެއްލެވީތީ ޝުކުރިއްޔާ has only 3 | The news corpus has too few sign-offs to decide (`reg_calque_thanks_order` already fixes the order) |
| ވަރަށް ބޮޑަށް ޝުކުރިއްޔާ | 1,015 | Attested, not an error |
| ހިނގާ ފަށަމާ / ފަށަމާ ހިނގާ | 20 / 87 | Both attested |
| ހަނދާން ނައްތާނުލާ vs ނައްތާނުލައްވާ | 49 vs 34 | A register question, not grammar; both attested |
| ހެޔޮ ދުވަހެއް | – | Already covered by `reg_calque_good_day` in register_rules.json |
| ފެންތައް, ފައިސާތައް, މުދާތައް | plural 2.3%, 3.4%, 7.9% of uses | Attested plurals ('funds', 'goods') |
| މަޢުލޫމާތުތައް, ހިޔާލުތައް, ތަޖުރިބާތައް, ކުލަތައް, އަގުތައް | 15–41% plural | Common, not errors |
| ރުފިޔާތައް | 236 | A real 'banknotes' sense in fiction. The numeral case is caught by rule 3 |
| ތަރައްގީތައް | 95 (0.5%) | 'Developments', a real plural in news |
| digit + plural | 1,514 of 3.09M | Years ('2020 މެޗްތައް') make it unsafe |
| honorific first-person past (…ކުރެއްވިން, …ކުރެއްވީމެވެ) | 1 after އަޅުގަނޑު, but 60 ކުރެއްވީމެވެ, mostly the divine "We" in Quran translation | Unsafe without context |

## Gating text before TTS

Install this package (`pip install -e path/to/dhivehi-rules`) and gate the text before it is
sent to any text-to-speech engine:

```python
import sys
from dhivehi_rules.script_gate import gate, gate_lines, check_script

gate(text, label="intro", context="ad")                               # SystemExit(2) on errors, prints fixes
gate_lines(lines_dict, context="video", force="--force" in sys.argv)  # many lines, one report
ok, report = check_script(text, "presenter")                          # never exits; inspect it yourself
# only after the gate passes: send text to TTS
```

From the shell, before any TTS run:

```
python -m dhivehi_rules.script_gate --context ad --file vo/lines.json && python your_tts_script.py
```

Gate the text you wrote. If the text is rewritten into the spoken register before synthesis, gate
the spoken form as well, because a rewrite can introduce errors. `--force` / `force=True` lets
errors through, prints a banner and appends the line to `logs/gate_overrides.log` in this
repository.
