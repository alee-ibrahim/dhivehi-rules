# Dhivehi orthography: the standard this repository enforces

This guide states which Dhivehi spellings are treated as correct, where each decision
comes from, and which rules a machine may apply on its own versus only report. The
code is in `dhivehi_rules/` and the data in `rules/`; book citations are in
`../SOURCES.md`.

## 1. The authority

The standard is the Dhivehi Academy's (ދިވެހިބަހުގެ އެކެޑަމީ, DBA):

| Topic | Book | Machine form |
|---|---|---|
| Dotted letters (thikijehi) | ތާނައިގައި ހުރި ނުކުތާޖެހި އަކުރުތައް ބޭނުންކުރާނެ ހަމަ, 2024 | `rules/dba_thikijehi_rules.json`, `dba_rules.check`, `dba_fix.fix` |
| Word division | ލަފުޒު ވަކިކޮށް ލިޔުމުގެ ގަވާއިދު, 2024 (supersedes the 2013 edition) | `dba_rules.check`, `dba_fix.fix` |
| Latin romanisation | official rules of 23 May 1977 | `thaana_latin.romanise` |
| Month names | Gazette announcement, 13 August 2013 | `rules/calendar.json` |
| Vocabulary | Radheef, the Academy's dictionary | `lexicon/radheef*.{jsonl,txt}` |

Where the corpus of real human writing (news, speeches, Majlis sittings;
`lexicon/corpus_vocab.tsv`) disagrees with a mechanical check, see section 6.

## 2. Dotted letters: the default is plain

The 2024 rules minimise thikijehi. Write the plain letter unless the word falls in a
protected category.

**Always reduce** (rule 5, the substitution table): ޘ→ސ, ޛ→ޒ, ޟ→ޒ, ޡ→ޒ, ޥ→ވ, ޜ→ޒ.

**Reduce in ordinary words** (rule 9, Radheef prefers the plain form): ޙ→ހ, ޞ→ސ, ޠ→ތ,
ޢ→އ, ޤ→ގ. Examples: ގައުމު not ޤައުމު, އުސޫލު not އުޞޫލު, އަސްލު not އަޞްލު,
ހަގީގަތް not ޙަޤީޤަތް, ގަވާއިދު, ހާސިލު, މަގުސަދު, ތަހުގީގު.

**Never drop** (rule 3): ޚ, ޣ, ޝ are Dhivehi sounds now: ޚަބަރު, ޚިޔާލު, މަޣުރިބު, މަޝްހޫރު.

**Keep the dots** in these cases (rules 1, 4, 6, 10):

- Homographs, where the dots decide the meaning: ޢަމަލު (deed) vs އަމަލު (intoxicant),
  ޚަބަރު (news) vs ހަބަރު, ވަޞީލަތް vs ވަސީލަތް, ޤާޟީ vs ޣާޒީ, plus the curated list in
  `homographs_keep_dots`. Derived forms keep the dots too: ޢަމަލީ, ޢަމަލުކުރުން.
- Hijri month names (`rules/calendar.json`).
- Arabic personal names in official text: ޢަބްދުއްރަޙުމާން, ޤާސިމް, ނާޡިމް.
- Arabic titles and positions: ޤާޟީ, ޢާމިލު, މުޙާމީ, ވަލީއަޙުދު.
- The names of Allah, Quran, hadith and salawat terms, and religious phrases, exactly as
  written: ޞައްލަﷲ ޢަލައިހި ޥަސައްލަމް.
- Titles written in Arabic form before names: އަލްފާޟިލް, އަލްފާޟިލާ. The name of Allah is
  written with the ligature ﷲ (މާތްﷲ), never spelled out.

Treat thikijehi beyond the book's named examples as soft. The older Radheef predates the
2024 rules (it lists ޤައުމު dotted), and the Academy's own 2024 books still write some
words dotted (ޤާނޫނު, ޚާއްޞަ, ޤައުމީ). This is why the checker reports thikijehi as warnings
and why the fixer reduces a dotted word only on evidence (section 4).

## 3. Word division (2024)

Rule ids in `dba_rules.check` cite the section of the 2024 book.

| Rule id | Section | Rule | Example |
|---|---|---|---|
| `5n_ordinal_split` | §5(ނ) | ވަނަ after a number (digits or words) is joined | 2021ވަނަ, not 2021 ވަނަ |
| `6sh_particle_joined` | §6(ށ) | these particles always stand apart: ވެސް, ނަމަވެސް, ފަދަ, ޓަކައި, ފިޔަވައި, މެނުވީ, ކަހަލަ | އަހަރު ވެސް, not އަހަރުވެސް |
| `6n_particle_split` | §6(ނ),(ރ) | plural and question particles are joined: ތައް, ތަކެއް, ތަކުގެ, ތަކަށް, ތަކުން, ހެއްޔެވެ, ތޯ | ދޮރުތައް |
| `6n_case_suffix` (fixer) | §6(ނ) | a case suffix is joined to its noun | ގާނޫނުގެ |
| `6b_negation_split` | §6(ބ) | negation prefixes ނު, ބަދު are joined | |
| `1k_reduplication_split` | §1(ކ), §2(ނ), §3(ށ) | a word repeated for plurality or intensity is one word, when the joined form is attested | |
| `7h_space_before_stop`, `7h_no_space_after_stop` | §7(ހ) | no space before a full stop; one space after it | ދިޔައީމެވެ. |
| `7n_padded_bracket` | §7(ނ) | no space inside brackets | |
| `7b_spaced_slash` | §7(ބ) | no space around a slash between Thaana words | |

Ambiguous surface forms are deliberately left alone: ގެ is both the genitive (joined)
and "house" (a word), ކަން both the "-ness" suffix and "matter", އެއް both the indefinite
and the numeral "one". Abbreviations written with stops (އެމް.ޑީ.ޕީ, އދ.ގެ) are correct.
A repeated word whose joined form is not attested (ރައީސް ރައީސް in a transcript) is a
duplicate, not reduplication, and is reported as `~duplicate_word`.

## 4. Auto-fix versus flag only

A fixer that changes correct text does more harm than no fixer. Each rule was audited on
random samples from the corpus before being allowed to correct text automatically.

**Safe to auto-fix** (`dba_fix.fix`):

| Rule | Audit |
|---|---|
| §6(ށ) non-attaching particle glued | 30/30, then 40/40 |
| §5(ނ) split ordinal | 30/30, then 40/40 |
| §6(ނ) particle split (with މެން excluded, since it is also English "men") | about 29/30, then 40/40 |
| §6(ނ) case suffix apart, only when the joined form occurs at least 20 times in the corpus and the word before is not a determiner or adjective | |
| §7 stop and bracket spacing, Thaana only | 25/25 |
| Thikijehi reduction, only where Radheef or the book has the plain form, or the plain form is in real use (at least 50 corpus occurrences and at least 25% of the dotted form's count) | 36/40 first pass; after fixing Quran terms, ޢަމަލ- derivatives and ވަލީއަޙުދު, 50/50 |

The thikijehi fixer protects ޚ ޣ ޝ, homographs and their derived forms, the sacred and
title prefixes in `KEEP_PREFIXES`, Hijri months, the names of Allah, anything containing ﷲ,
personal names (`rules/protected_names.json`, found by their position after a title or on
a speaker line) and any dotted word next to a title or a protected name. Names are matched
by an inflection-aware stem, so ޢިމްރާނަކީ is protected as ޢިމްރާން.

**Flag only, never auto-fix**:

- §1(ކ) reduplication: about 19/30 correct in audit (typos and Hindi titles look the same).
- §6(ބ) negation: about 6/30 before it was narrowed to ނު and ބަދު (ނޫ is "blue", ބޭ is "Bay"
  in place names, ނާ/ނޭ occur in Hindi titles). Still not auto-fixed.
- Thikijehi warnings outside the evidence threshold.
- Register and grammar rules (`rules/register_rules.json`, `rules/grammar_rules.json`): these
  give a suggested form, but a person applies it.

The fixer is idempotent: running it twice changes nothing the second time.

## 5. Romanisation (23 May 1977)

`thaana_latin.romanise` implements the official rules and reproduces all 68 examples in the
booklet (`python -m dhivehi_rules.thaana_latin --test`).

- §1 consonants: ހ h, ށ sh, ނ n, ރ r, ބ b, ޅ lh, ކ k, ވ v, މ m, ފ f, ދ dh, ތ th, ލ l, ގ g, ޏ gn,
  ސ s, ޑ d, ޒ z, ޓ t, ޔ y, ޕ p, ޖ j, ޗ ch.
- §2 Arabic letters: ޞ s', ޟ l', ޠ t', ޡ z', ޥ w, ޘ th', ޙ h', ޚ kh, ޛ dh', ޣ gh, ޤ q. ޝ is written
  sh, as the booklet's own ނިޝާން = nishaan does. ޢ is the vowel with an apostrophe: a'mal.
- §3 vowels: ަ a, ާ aa, ި i, ީ ee, ު u, ޫ oo, ެ e, ޭ ey, ޮ o, ޯ oa; އ + vowel is the vowel alone.
- §4 sukun: final އް → h (meeheh), ން → n (fen), ށް → iy (foiy), ސް → s (gas). Before a consonant,
  އް doubles it (bappa, bayyeh) and ން before މ is m (mamma).
- §5 a bare ނ before a consonant (prenasalisation) is n' (kan'di, an'bu).
- §6 a sentence begins with a capital.

Not automated: capitals for proper nouns (Thaana has no case), §8's rule that English words
keep their English spelling (ޓިކެޓް is "ticket"), and Arabic loans that drop a final vowel.
The 1977 booklet's own Latin text writes ge/gai as separate words; that is 1977 Latin
practice and says nothing about Thaana word division today.

## 6. Writing new Dhivehi: verification rules

These apply to any Dhivehi that was not written by a native speaker, including
machine-written and machine-translated text.

1. **No invented words.** Check every word against Radheef headwords and the corpus
   vocabulary (`lexicon/radheef_headwords.txt`, `lexicon/corpus_vocab.tsv`). A word in neither
   is presumed invented until a native speaker confirms it.
2. **No calques.** A sentence can consist entirely of real words and still be a word-for-word
   translation that no Maldivian would write. A dictionary check cannot catch this; only
   human-written Dhivehi or native review can. Prefer human-written source text.
3. **Loanwords as they sound.** If Dhivehi has no word for a term, write the loanword the way
   it is pronounced (އެލްގޮރިޒަމް). Do not coin a word or translate the parts.
4. **Prefer attested forms.** When writing a phrase yourself, pick forms that occur in the
   corpus. Example: ބައްލަވާލައްވާށެވެ, އެހީތެރިވެދޭނަން, ރޮބޮޓެއް are attested;
   ބަލާލައްވާށެވެ, އެހީތެރިވެދެމެވެ, ރޯބޯޓެއް are not.
5. **The corpus beats the validator on common words.** `thaana.validate` is stricter than real
   usage in places: human text writes ޔުނިވަރސިޓީ (3,904 occurrences) and never ޔުނިވަރްސިޓީ.
   When the validator and the corpus disagree on a common word, follow the corpus.
6. **Check before speech.** No Dhivehi goes to text-to-speech without passing
   `dhivehi_rules.script_gate` (Thaana validity, DBA rules, register, grammar). Pronunciation
   rules for TTS are in `rules/pronunciation.json`; they describe how text is read, not how
   it is written.

## 7. Dates and numbers

Use the official month forms in `rules/calendar.json` (ސެޕްޓެންބަރު, not ސެޕްޓެމްބަރު or
ސެޕްޓެމްބަރ); the common non-standard forms are listed there for recognition only. Number
words, with the standalone and pre-noun forms, are in `rules/numbers.json`.
