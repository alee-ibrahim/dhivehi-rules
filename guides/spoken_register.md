# Spoken register for audience-facing Dhivehi: ads, presenters, video

`dhivehi_rules/thaana.py` checks that Thaana is well formed. `dhivehi_rules/dba_rules.py` checks the
Academy's spelling and word-division rules. Neither one can tell a scripture translation from a
TV host. A script can pass both and still sound wrong to a Maldivian. This guide covers that
gap: who "you" and "I" are, how to ask the audience to do something, and English phrasings that
do not carry over into Dhivehi.

The machine-checkable part is in `rules/register_rules.json`. Run it with:

    python -m dhivehi_rules.dba_rules --context presenter "<script>"     # or ad / video

Use `--context` on any text written for viewers. Without `--context` the register rules do not run.

## Evidence base

Counts come from a corpus of real Dhivehi writing and speech. They are not from a style manual.

| Source | Docs | Register |
|---|---|---|
| Public speeches | 469 | Spoken Dhivehi addressed to an audience, the closest match to a presenter |
| Majlis sittings | 92,958 | Formal spoken (transcribed) |
| News, 8 sites (sun, mihaaru, avas, psmnews, raajje, vaguthu, dhauru, khabaru) | 609k | Written. Includes quotes, fiction, opinion and religious columns, and about 25k promotional items (telco, bank and shop promotions written as news) |
| Phrase counts, all 26 news sites | about 1.0M | Used for ad phrasing: CTA, price, delivery |

"Promotional items" means news documents that mention WhatsApp, a hotline, delivery, a promotion,
a discount, an offer, Viber or customers. These were mined on 2026-10-15. The counts are
reproducible with a plain regex scan of the sources above.

## 1. Addressing the audience ("you")

| Form | Speeches | Majlis | News | In promotional items | Verdict for ad/presenter |
|---|---:|---:|---:|---:|---|
| **ތިޔަބޭފުޅުން** (joined) | **2,595** | 566 | 1,572 | 70 | **Use this.** It is the standard polite plural "you" |
| ތިޔަ ބޭފުޅުން (spaced) | 11 | 937 | 1,258 | 58 | Same word. Speeches write it joined, so prefer joined |
| **ހުރިހާ ބޭފުޅުން(ނަށް ވެސް)** | 660 | 4,033 | 2,675 | 129 | **Use** for "everyone". Example: "ހުރިހާ ބޭފުޅުންނަށް ވެސް މަރުހަބާ" |
| ތިޔަބައިމީހުން | 114 | 140 | 4,680 | 26 | **Don't.** Scripture register (see below) |
| ތިބާ | 4 | 47 | 5,931 | 203 | Avoid in speech. Written generic "you/one" from slogans and advice columns |
| ކަލޭ / ކަލޭމެން | 23 | 969 | 17,864 | 574 | **Never.** Intimate or rude. News hits are quoted dialogue and fiction |

**Why ތިޔަބައިމީހުން is wrong.** It is the "O you people" of Quran and hadith translations. In
the news corpus, 70% of its uses (3,263 of 4,680) are in a sentence that also quotes or cites
scripture (Arabic text, ﷲ, ކަލާނގެ, ރަސޫލު, ހަދީސް, އާޔަތް). Example: "ތިޔަބައިމީހުން މިނުމާއި،
ކިރުން، ޢަދުލަށް ފުރިހަމަކުރާށެވެ!" (sun.mv/206055). Speakers who address a live audience use
ތިޔަބޭފުޅުން about 23 times as often.

**Real usage of ތިޔަބޭފުޅުން in promotional copy:**
- Ooredoo: "އަޅުގަނޑުމެން ތިޔަބޭފުޅުންނަށް މި ގެނެސްދެނީ..." (raajje.mv/163613)
- A company statement: "މިއީ ތިޔަބޭފުޅުންގެ އެހީތެރިކަމާއެކު..." (sun.mv/207779)
- A business, quoted: "އަޅުގަނޑުމެން ތިޔަ ބޭފުޅުންގެ މުދާ ޑެލިވަރީ ކޮށްދޭނަން." (avas.mv/80108)

## 2. Referring to yourself ("I" and "we")

| Form | Speeches | Majlis | Verdict |
|---|---:|---:|---|
| **އަޅުގަނޑު** (and އަޅުގަނޑަށް, އަޅުގަނޑުގެ…) | **16,614** | 586,790 | **Use.** The public, polite "I" |
| އަހަރެން / އަހަންނަށް | 13 | 148 | **Don't** in public speech |
| **އަޅުގަނޑުމެން** | **20,315** | 529,685 | **Use** for the business: "އަޅުގަނޑުމެންގެ ކަސްޓަމަރުން" appears 279 times in promotional items |
| އަހަރެމެން | 24 | 212 | Don't |
| ތިމަންނަ | 171 | 8,782 | Avoid. This is the "I" of official letters and statements |

The 1:1,000-plus ratios in speech are the key fact. Written news does contain plenty of
އަހަރެން, but in short stories, diaries, and translations of foreign people's quotes (for
example psmnews.mv/86286, a story, and dhauru.com/post/business/9585, Zuckerberg translated).
Maldivian speakers quoted in the same papers say އަޅުގަނޑު.

## 3. Asking the audience to act (imperatives, CTA)

Use the honorific (ވަޑައިގަންނަވާ-level) verb forms. The plain imperative is for children and
close friends.

| Say | Not | Evidence |
|---|---|---|
| (number) އަށް **ގުޅުއްވާ** / ގުޅުއްވުމުން | ގުޅާ | 1,396 vs 275 after a 7-digit number. Most of the plain uses are reported instructions |
| **ބައްލަވާ**, **ބައްލަވާލައްވާ** | ބަލާ, ބަލާލާ | ބައްލަވާ 4,710 in news |
| **ވަޑައިގަންނަވާ** / ފިހާރައަށް ވަޑައިގެން | އަންނަ / ދާ (to the viewer) | 5,145 |
| **ހޯއްދަވާ**, ހޯއްދެވޭނެ | ހޯދާ (to the viewer) | 4,046 / 133 |
| **ގަންނަވަން ބޭނުންފުޅުވާ** ބޭފުޅުން | ގަންނަން ބޭނުން މީހުން | 286 |
| **އޯޑަރުކުރެއްވުމަށް**, އޯޑަރުކުރެއްވޭނެ | އޯޑަރ ކުރޭ | 61 / 10 |
| ...**ކުރައްވާ** (sentence-final polite request) | ...ކުރޭ | |

**WhatsApp.** Real copy says **ވަޓްސްއެޕް މެދުވެރިކޮށް** (253 hits) with a real verb, for example
"ވަޓްސްއަޕް (WhatsApp) މެދުވެރިކޮށް ވެސް މެސެޖުކުރައްވައިގެން އޯޑަރު ކުރެއްވޭނެއެވެ" (halinews).
"ވަޓްސްއެޕް ކުރައްވާ" appears once. Casual speech does say "ވަޓްސްއެޕް ކޮށްލައްވާ", so the
checker only warns on it.

**"For more information":** "އިތުރު މަޢުލޫމާތު ސާފުކުރެއްވުމަށް / ހޯއްދެވުމަށް ... ގުޅުއްވާ" (567 hits).

## 4. Price, delivery, colours

- **Price:** "އަގު ހަމައެކަނި X ރުފިޔާ" and "X ރުފިޔާއަށް ލިބޭނެ" (130). "ހަމައެކަނި 495 ރުފިޔާއަށް..." (avas).
  "X ރުފިޔާއިން ފެށިގެން" (246) means "from X".
- **Free delivery:** **ހިލޭ ޑެލިވަރީ** (399). The modifier goes first. "ޑެލިވަރީ ހިލޭ" and
  "ޑެލިވަރީ ފްރީ" appear **0** times. "ފްރީ ޑެލިވަރީ" (114) is mostly the film title. Real copy
  says "...ހިލޭ ޑެލިވަރީ ކޮށްދޭނެއެވެ".
- **Silver colour:** **ރިހި ކުލަ** (360) is far more common than ސިލްވަރ ކުލަ (12). Black is ކަޅު ކުލަ.

## 5. Greeting and sign-off

- Opening: "އައްސަލާމް ޢަލައިކުމް" (news 261, plus 1,941 written joined in Majlis records), then
  "ހުރިހާ ބޭފުޅުންނަށް ވެސް މަރުހަބާ". The checker gives a soft `~thikijehi` note on ޢަލައިކުމް.
  This is a religious formula, and most of the corpus keeps the ޢ.
- Closing, from real TV sign-offs: "**ބެއްލެވީތީ ޝުކުރިއްޔާ**". The reason comes first, then the thanks.
  - "ޚަބަރު ބެއްލެވީތީ ޝުކުރިއްޔާ.. އެންމެ ބޭފުޅުންނަށް ވެސް ބާއްޖަވެރި، އަމާން، ރައްކާތެރި ރެޔަކަށް..." (esfiya)
  - "ބާއްޖަވެރި ރޭގަނޑަކަށް އެދެން ޕޮރުގުރާމު ބެއްލެވީތީ ޝުކުރިއްޔާ." (esfiya)
- Wishes: **ބާއްޖަވެރި ދުވަހަކަށް / ރޭގަނޑަކަށް އެދެން** (120). Do not use "ހެޔޮ ދުވަހެއް" or
  "ހެޔޮ ހެނދުނެއް". These are word-for-word "good day / good morning" and appear 5 times, none as a greeting.

## 6. Literal translations and coinages to avoid

| Avoid | Why | Use |
|---|---|---|
| ތިޔަބައިމީހުން | Scripture register | ތިޔަބޭފުޅުން / ހުރިހާ ބޭފުޅުން |
| އަހަރެން, އަހަރެމެން | Private/narrative "I" | އަޅުގަނޑު, އަޅުގަނޑުމެން |
| ޑެލިވަރީ ފްރީ / ހިލޭ | English word order | ހިލޭ ޑެލިވަރީ |
| ޝުކުރިއްޔާ ބެއްލެވީތީ | English word order | ބެއްލެވީތީ ޝުކުރިއްޔާ |
| ހެޔޮ ދުވަހެއް | Calque | ބާއްޖަވެރި ދުވަހަކަށް އެދެން |
| ފެންފައިޕު ("faucet") | 0 hits in corpus and Radheef | Product name (ޕުލް އައުޓް ފޯސެޓް) or ބާވަތް. See note |
| މަލަ ނާރާ ("rust-proof") | The one hit is a mis-split of ހަމަލަ | State the material: ސްޓެއިންލެސް ސްޓީލުން ހަދާފައިވާ |
| ވަޓްސްއެޕް ކުރައްވާ | English verb | ވަޓްސްއެޕް މެދުވެރިކޮށް މެސެޖުކުރައްވާ |

**Faucet/tap.** The written corpus has no settled Dhivehi word for a kitchen tap. ޓޭޕް/ޓޭޕު
(about 450 hits) is adhesive or recording tape. ފޯސެޓް occurs only in machine-translated instruction
data and a few news items. ފެނުގެ ހޮޅި means a water pipe. Name the product, then refer to it
as "މި ބާވަތް" or by its parts. A native speaker should decide on any everyday word for the tap.

## 7. Spelling still applies

Register rules sit on top of the Academy rules. They do not replace them. Verbs formed with
ކުރުން are written joined (§2(ށ)): މެސެޖުކުރައްވާ, އޯޑަރުކުރެއްވުމަށް. Question ތޯ is joined.
Loanwords end in a fili: ސިލްވަރު, not ސިލްވަރ. Run both checks:

    python -m dhivehi_rules.dba_rules --context ad "<text>"     # spelling + division + register
    python -c "from dhivehi_rules import thaana as T; print(T.validate(open('f.txt',encoding='utf-8').read()).orthography_errors)"

## Grammar and the TTS gate

Register is only one layer. Corpus-backed grammar rules (existential verb agreement such as
ސުވާލެއް **އޮތް** ނަމަ, honorific verbs with first-person endings, plurals after numerals, ނަމަ/ނަމަވެސް)
are in `rules/grammar_rules.json`, with the evidence in `guides/grammar.md`. They run whenever `--context` is
given. **No Dhivehi text goes to TTS without passing `dhivehi_rules/script_gate.py`**, which runs
thaana.validate, the DBA rules, these register rules and the grammar rules, and exits 2 on any error.

## Limits

- None of the corpus is broadcast-ad transcription. The closest material is public speeches,
  promotional news items and quoted TV sign-offs. Facebook and Instagram shop posts were not
  available to crawl.
- The checker is surface-level. It can't tell a quoted villain's ކަލޭ from the presenter's own
  words. Don't run it with a context on fiction or quotes.
- Severity `warn` (shown with a leading `~`) means a native speaker should judge it in context.
  Severity `error` means it was never seen addressing an audience in the evidence above.
