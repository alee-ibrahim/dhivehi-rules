"""
Checks Dhivehi text against the Dhivehi Academy's writing standards.

`thaana.validate` checks that Thaana is well-formed -- every consonant carries
a fili or sukun, no orphan or doubled marks. It says nothing about whether the
text is written the way the Academy prescribes. This does, for the parts of
the standard a machine can check without understanding the sentence:

  ލަފުޒު ވަކިކޮށް ލިޔުމުގެ ގަވާއިދު (2024)  -- which words are joined, which apart
  ތާނައިގައި ހުރި ނުކުތާޖެހި އަކުރުތައް ބޭނުންކުރާނެ ހަމަ (2024)  -- dotted letters

Source texts: the DBA books cited in SOURCES.md, and rules/dba_thikijehi_rules.json. Rule
ids below cite the section of the 2024 word-division book (e.g. "5n" = §5(ނ)).

Every rule is deliberately narrow. A checker that flags correct text teaches
nothing and, used as a filter, throws good data away, so each pattern is
limited to the cases the book states outright, and ambiguous surface forms are
left alone: ގެ is both the genitive (joined) and "house" (a word), ކަން both
the -ness suffix (joined) and "matter" (a word), އެއް both the indefinite
(joined) and the numeral "one" (apart). None of those are flagged as a
standalone token.

    python -m dhivehi_rules.dba_rules "އަހަރެންވެސް 14 ވަނަ ދުވަހު ދިޔައީމެވެ ."
    python -m dhivehi_rules.dba_rules --file corpus.jsonl --field messages

Register. Spelling can be perfect and the text still wrong for its audience:
ތިޔަބައިމީހުން is scripture, އަހަރެން is a diary. Given a context (ad,
presenter, video), check() also applies rules/register_rules.json -- word
choice for speech addressed to viewers; evidence in guides/spoken_register.md.
Without a context those rules do not run.

    python -m dhivehi_rules.dba_rules --context presenter "މިއަދު އަހަރެން ތިޔަބައިމީހުންނަށް ދައްކާލާނީ"

Grammar. rules/grammar_rules.json holds corpus-backed rules for the errors
an LLM makes in Dhivehi: existential verb agreement (ސުވާލެއް އޮތް, not ސުވާލެއް
ހުރި; ކުދިން ތިބި), honorific verbs with a first-person ending, plurals after
numerals and on uncountables, and ނަމަ/ނަމަވެސް. They run whenever a context is
given, or with --grammar; evidence is in guides/grammar.md. Before TTS, use
dhivehi_rules.script_gate, which runs all of the above and exits non-zero on errors.

    python -m dhivehi_rules.dba_rules --grammar "ސުވާލެއް ހުރި ނަމަ"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent      # repo root: rules/, lexicon/
if __package__ in (None, ""):                       # run as a plain script
    sys.path.insert(0, str(ROOT))
from dhivehi_rules import thaana as T  # noqa: E402

TH = "ހ-޿"
WORD = rf"[{TH}]+"

# §5(ނ) "ވަނަ" after a number, digits or words, is joined to it.
NUMBER_WORDS = ("އެއް", "ދެ", "ތިން", "ހަތަރު", "ފަސް", "ހަ", "ހަތް", "އަށް", "ނުވަ",
                "ދިހަ", "އެގާރަ", "ބާރަ", "ތޭރަ", "ސާދަ", "ފަނަރަ", "ސޯޅަ", "ސަތާރަ",
                "އަށާރަ", "ނަވާރަ", "ވިހި", "ތިރީސް", "ސާޅީސް", "ފަންސާސް", "ފަސްދޮޅަސް",
                "ހައްދިހަ", "ހަތްދިހަ", "އަށްޑިހަ", "ނުވަދިހަ", "ސަތޭކަ", "ހާސް")
# §6(ށ) particles that never attach -- always written apart from the word before.
NON_ATTACHING = ("ނަމަވެސް", "ވެސް", "ފަދަ", "ޓަކައި", "ފިޔަވައި", "މެނުވީ", "ކަހަލަ")
# §6(ނ),(ރ) plural and question particles -- always joined to the word before.
# "މެން" is left out: it is also English "men" in transliterated titles.
JOIN_AFTER = ("ތައް", "ތަކެއް", "ތަކުގެ", "ތަކަށް", "ތަކުން", "ހެއްޔެވެ", "ހެއްޔޭ", "ތޯ")
# §6(ބ) negation prefixes, when written as a separate token. Only the two that
# are never words on their own: ނޫ is also "blue", ބޭ is "Bay" in place names,
# ނާ/ނޭ occur in Hindi titles -- a random audit found 6 of 30 hits correct
# with them in.
NEG_PREFIX = ("ނު", "ބަދު")

_RE = {
    "5n_ordinal_split": re.compile(
        rf"(?:\d+|(?<![{TH}])(?:{'|'.join(NUMBER_WORDS)}))[ \t]+ވަނަ(?![{TH}])"),
    "6n_particle_split": re.compile(
        rf"(?<=[{TH}])[ \t]+(?:{'|'.join(JOIN_AFTER)})(?![{TH}])"),
    "6b_negation_split": re.compile(
        rf"(?<![{TH}])(?:{'|'.join(NEG_PREFIX)})[ \t]+(?=[{TH}])"),
    "7h_space_before_stop": re.compile(rf"(?<=[{TH}])[ \t]+\.(?!\d)"),
    # A full stop glued to the next word. Not inside an abbreviation: in
    # އެމް.ޑީ.ޕީ or އދ.ގެ the stops belong to the abbreviation and the standard
    # writes them solid (§7(ޅ)). What is left is the title case -- ޑރ.މުޢިއްޒު,
    # which the Academy's own books write "ޑރ. އަޝްރަފް" -- and a sentence run
    # into the next. The lookbehind requires a word of 3+ letters before the
    # stop (so not a 1-2 letter abbreviation piece like ޕީ or އދ) or the title ޑރ.
    "7h_no_space_after_stop": re.compile(
        rf"(?:(?<![{TH}.])[{TH}]{{3,}}|(?<![{TH}])ޑރ)\.(?=[{TH}]{{2,}})(?![{TH}]*\.)"),
    "7n_padded_bracket": re.compile(r"\([ \t]+|[ \t]+\)"),
    "7b_spaced_slash": re.compile(rf"(?<=[{TH}])[ \t]+/|/[ \t]+(?=[{TH}])"),
}


@lru_cache(maxsize=1)
def radheef_words() -> frozenset[str]:
    p = ROOT / "lexicon" / "radheef_headwords.txt"
    return frozenset(T.normalise(w) for w in p.read_text(encoding="utf-8").splitlines()
                     if w.strip()) if p.exists() else frozenset()


_FOLD = str.maketrans({"ޘ": "ސ", "ޛ": "ޒ", "ޟ": "ޒ", "ޡ": "ޒ", "ޥ": "ވ", "ޜ": "ޒ",
                       "ޙ": "ހ", "ޞ": "ސ", "ޠ": "ތ", "ޢ": "އ", "ޤ": "ގ"})


@lru_cache(maxsize=1)
def thikijehi_rules() -> dict:
    return json.loads((ROOT / "rules" / "dba_thikijehi_rules.json")
                      .read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def homographs() -> frozenset[str]:
    return frozenset(thikijehi_rules()["homographs_keep_dots"]["words"])


@lru_cache(maxsize=1)
def thikijehi_twins() -> dict[str, str]:
    """Dotted headword -> its plain twin, where Radheef lists both (rule 9: plain wins).

    Minus the homographs, where the two spellings are two different words and
    rule 1 keeps the dots (ޢަމަލު "deed" is not އަމަލު "intoxication").
    """
    words, keep = radheef_words(), homographs()
    return {w: w.translate(_FOLD) for w in words
            if w not in keep and w.translate(_FOLD) != w and w.translate(_FOLD) in words}


@lru_cache(maxsize=1)
def named_examples() -> dict[str, str]:
    """Dotted -> plain for the words the 2024 thikijehi book names outright.

    Needed because the Radheef we have (app v2.1.6) predates the 2024 rules and
    lists some of these dotted only -- ޤައުމު, ޙަޤީޤަތް -- the very words the
    Academy now gives as examples of writing plain.
    """
    ex = thikijehi_rules()["radheef_prefers_plain_examples"]
    pairs = {dotted: plain for plain, dotted in ex.items() if not plain.startswith("_")}
    for plain in ex.get("_more_plain", []):
        dotted = {"ގަވާއިދު": "ޤަވާޢިދު", "ހާސިލު": "ޙާޞިލު",
                  "މަގުސަދު": "މަޤްޞަދު", "ތަހުގީގު": "ތަޙުޤީޤު"}.get(plain)
        if dotted:
            pairs[dotted] = plain
    return pairs


@lru_cache(maxsize=1)
def exception_words() -> frozenset[str]:
    """Words the standard requires dotted: names, months, titles, Allah's names."""
    r = thikijehi_rules()
    out = set(homographs())
    req = r["required_thikijehi"]
    for key in ("hijri_months", "arabic_personal_names_in_official_text",
                "arabic_titles_positions", "names_of_allah_99"):
        for w in req.get(key, []):
            out.update(w.split())
    for w in r["exceptions_write_arabic"]["titles_before_names"]:
        out.add(w)
    return frozenset(out)


_REDUCIBLE = set("ޘޛޟޡޥޜޙޞޠޢޤ")


def reducible_dotted(word: str) -> bool:
    """Rule 2's default: a dotted word not in any exception is written plain.

    'Probable', not certain -- an Arabic personal name in running text looks
    exactly like this, and the standard keeps names dotted.
    """
    return bool(_REDUCIBLE & set(word)) and word not in exception_words() \
        and "ﷲ" not in word and not plain_preferred(word)


def plain_preferred(word: str) -> str | None:
    """The plain spelling the standard prefers for this dotted word, if any.

    Rule 9: check Radheef and write the word as Radheef has it; where Radheef
    has it plain -- whether or not it also lists the dotted form -- plain wins.
    A dotted word Radheef does not know, whose plain form it does not know
    either, is a name or a required religious form and is left alone.
    """
    if word in homographs():
        return None
    folded = word.translate(_FOLD)
    if folded == word:
        return None
    if word in named_examples():
        return named_examples()[word]
    if word in thikijehi_twins():
        return thikijehi_twins()[word]
    if word not in radheef_words() and folded in radheef_words():
        return folded
    return None


@lru_cache(maxsize=1)
def attested_joined() -> frozenset[str]:
    """Reduplicated forms (ww) the corpus writes joined at least 5 times."""
    p = ROOT / "lexicon" / "corpus_vocab.tsv"
    out = set()
    if p.exists():
        for line in p.open(encoding="utf-8"):
            w = line.split("\t", 1)[0]
            h = len(w) // 2
            if len(w) >= 4 and len(w) % 2 == 0 and w[:h] == w[h:]:
                out.add(w)
    return frozenset(out)


# Case and derivational endings, longest first, for finding the stem of an
# inflected dotted word: ޤައުމުގެ, ޤައުމަށް, ޤާނޫނަށް are the same ޤައުމު/ޤާނޫނު.
_STEM_ENDINGS = ("ތަކުގައި", "ތަކުގެ", "ތަކަށް", "ތަކުން", "ތައް", "ގައި", "އަކީ", "އަށް",
                 "އިން", "އާއި", "އެއް", "ގެ", "ށް", "ން", "އާ", "އީ", "ކަން", "ކޮށް")


def stems(word: str):
    yield word
    for e in _STEM_ENDINGS:
        if word.endswith(e) and len(word) - len(e) >= 3:
            base = word[: -len(e)]
            yield base
            # The dative turns a final ު into ަ (ޤައުމު -> ޤައުމަށް), and some
            # endings drop it altogether; both are put back to find the headword.
            if base.endswith("ަ"):
                yield base[:-1] + "ު"
            elif not base.endswith(("ު", "ި", "ާ", "ީ", "ެ", "ޫ", "ް")):
                yield base + "ު"


@dataclass
class Hit:
    rule: str
    span: str
    fix: str = ""          # suggested replacement, register and grammar rules only
    why: str = ""          # one-line reason with the corpus evidence, grammar rules only


@lru_cache(maxsize=1)
def register_rules() -> dict:
    return json.loads((ROOT / "rules" / "register_rules.json")
                      .read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def _register_rx(context: str) -> tuple:
    rules = register_rules()
    if context not in rules["contexts"]:
        raise ValueError(f"unknown context {context!r}; one of {sorted(rules['contexts'])}")
    return tuple((("~" if r["severity"] == "warn" else "") + r["id"],
                  re.compile(r["pattern"]), r.get("replace", ""))
                 for r in rules["rules"] if context in r["contexts"])


def register_check(text: str, context: str) -> list[Hit]:
    """Word choice for speech addressed to an audience (ad, presenter, video)."""
    return [Hit(rule, m.group(0), m.expand(rep) if rep else "")
            for rule, rx, rep in _register_rx(context) for m in rx.finditer(text)]


@lru_cache(maxsize=1)
def grammar_rules() -> dict:
    return json.loads((ROOT / "rules" / "grammar_rules.json")
                      .read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _grammar_rx() -> tuple:
    return tuple((("~" if r["severity"] == "warn" else "") + r["id"],
                  re.compile(r["pattern"]), r.get("replace", ""), r.get("why", ""))
                 for r in grammar_rules()["rules"])


# Existential/locative verbs, by class. The same token classes as the corpus
# miner that produced the counts in grammar_rules.json (see guides/grammar.md):
# a token is a verb of a class if, after an optional އެބަ, it starts with one of
# the stems -- unless it starts with one of _EXIST_NOT (ހުރިހާ "all", ހުރުމަތް
# "respect", honorific ހުންނެވި/ތިއްބެވި-type forms, ތިބޭފުޅުން "you", the
# potential ހުރެވ-). Plain ހުއްޓޭ is also "stops", so only އެބަހުއްޓޭ counts.
_EXIST_STEMS = {
    "huri": ("ހުރި", "ހުރީ", "ހުރެ", "ހުރޭ", "ހުރުމ", "ހުރުން", "ހުންނަ", "ހުންނާ", "ހުއްޓެވެ", "ހުއްޓޭ"),
    "oth": ("އޮތް", "އޮތީ", "އޮތެ", "އޮތު", "އޮތޭ", "އޮތި", "އޮވެ", "އޮވޭ", "އޮންނަ", "އޮންނާ"),
    "thibi": ("ތިބި", "ތިބީ", "ތިބެ", "ތިބޭ", "ތިބު", "ތިއްބެ", "ތިއްބަ"),
}
_EXIST_NOT = ("ހުރިހާ", "ހުރިހައި", "ހުރުމަތް", "ހުންނަވ", "ހުންނެވ", "ތިބޭފުޅ", "ހުރެވ", "އޮވެވ", "ތިބެވ")
_EXIST_BARE = {"ހުރި": "huri", "ހުންނަ": "huri", "އޮތް": "oth", "އޮންނަ": "oth",
               "ތިބި": "thibi", "ތިބޭ": "thibi"}
# A word ending in one of these is not the verb's subject (a locative, genitive,
# dative, ablative...), so the word before the verb is skipped.
_EXIST_OBLIQUE = ("ގައި", "ގަ", "ގެ", "އަށް", "ށް", "ން", "އާ", "އާއި", "ތެރޭ", "ކައިރީ", "މަތީ",
                  "ދޮށު", "ކަމަށް", "ކަން", "ހެން", "ފަދަ", "ވެސް", "އަކީ", "އީ", "ތީ")
# Words that close the clause after a participle: 'ސުވާލެއް ހުރި ނަމަ'. A participle
# followed by anything else may be modifying the next noun instead.
_CLAUSE_PARTICLES = frozenset(("ނަމަ", "ނަމަވެސް", "ކަމަށް", "ކަމަށެވެ", "ކަމުގައި", "ކަން", "ކަމާ",
                               "ކަމެވެ", "އިރު", "އިރުގައި", "ތޯ", "ތޯއެވެ", "ހެން", "ފަދަ", "އެވެ", "ވެސް",
                               "ކަމުން", "ކަމަށާއި", "ކަމާއި", "ކަމަކީ", "ހިނދު", "ތާ", "ތަނާ"))
# Word endings before a participle that leave it without a subject of its own, for
# the relative check. _EXIST_OBLIQUE minus -ން (ގުޅުން is a noun, not an
# ablative), plus the comitative -ނާ.
_REL_OPENERS = tuple(e for e in _EXIST_OBLIQUE if e != "ން") + ("ނާ",)
_EXIST_NAME = {"huri": "ހުރި", "oth": "އޮތް", "thibi": "ތިބި"}
_NUM_NAME = {"sgi": "indefinite singular", "sg": "bare", "pl": "plural"}


def _exist_class(t: str) -> str | None:
    if t.startswith("ހުއްޓޭ"):
        return None
    b = t[3:] if t.startswith("އެބަ") else t
    if b.startswith(_EXIST_NOT):
        return None
    return next((k for k, st in _EXIST_STEMS.items() if b.startswith(st)), None)


def _exist_key(t: str) -> tuple[str, str]:
    """(key, number) for a noun token, exactly as the miner computed them."""
    num = "sg"
    if t.endswith(("ތަކެއް", "ތައް", "ތަކެތި")):
        num = "pl"
        t = t[: -len(next(e for e in ("ތަކެއް", "ތައް", "ތަކެތި") if t.endswith(e)))]
    elif t.endswith("އެއް"):
        t, num = t[:-4], "sgi"
    elif t.endswith("ެއް"):
        t, num = t[:-3], "sgi"
    elif t.endswith(("މީހުން", "ކުދިން", "ބޭފުޅުން", "މެން", "ހުން", "ދިން")):
        num = "pl"
    if t.endswith(("ު", "ް")):
        t = t[:-1]
    return t, num


def _exist_swap(verb: str, target: str) -> str:
    """The same verb form in another class: ހުރިނަމަ -> އޮތްނަމަ, އެބަހުރި -> އެބައޮތް."""
    pre, b = ("އެބަ", verb[3:]) if verb.startswith("އެބަ") else ("", verb)
    col = {"huri": 0, "oth": 1, "thibi": 2}[target]
    for forms in grammar_rules()["existential"]["verb_forms"]:
        for f in forms:
            if b.startswith(f):
                return pre + forms[col] + b[len(f):]
    return ""


def _exist_judge(counts: dict, used: str, section: str = "existential"):
    """(preferred verb, severity) if the corpus says `used` is wrong here, else None."""
    th = grammar_rules()[section]["thresholds"]
    tot = sum(counts.values())
    if tot < th["min_n"]:
        return None
    best = max(counts, key=counts.get)
    share = counts[best] / tot
    if best == used or share < th["min_share"] or counts.get(used, 0) / tot > th["max_used_share"]:
        return None
    sev = "error" if share >= th["error_share"] and tot >= th["error_n"] else "warn"
    return best, sev


def _exist_counts(noun_tok: str, pos: str, used: str = "huri"):
    """(counts, label, section) for a noun token in a position, or None."""
    human = grammar_rules()["human_plural"]["nouns"]
    if pos == "pred" and noun_tok in human:
        if used != "huri":
            return None     # 'ރައްޔިތުން އޮތީ ނޫނެކޭ ބުނެފަ' is the stative focus construction
        return human[noun_tok]["pred"], f"{noun_tok} (human plural)", "human_plural"
    nouns = grammar_rules()["existential"]["nouns"]
    key, num = _exist_key(noun_tok)
    counts = nouns.get(key, {}).get(num, {}).get(pos)
    return (counts, f"{nouns[key]['noun']} ({_NUM_NAME[num]})", "existential") if counts else None


def exist_check(text: str) -> list[Hit]:
    """Noun / existential-verb agreement: ސުވާލެއް އޮތް, not ސުވާލެއް ހުރި."""
    human = grammar_rules()["human_plural"]["nouns"]
    toks = re.findall(rf"{WORD}|[.!?؟،,]", text)
    hits = []

    def judge(noun_tok, verb_tok, used, pos, span, fix_of):
        found = _exist_counts(noun_tok, pos, used)
        res = found and _exist_judge(found[0], used, found[2])
        if not res:
            return
        (counts, label, _), (best, sev) = found, res
        why = (f"{label} takes {_EXIST_NAME[best]}: corpus {_EXIST_NAME[best]} {counts[best]:,} "
               f"vs {_EXIST_NAME[used]} {counts[used]:,} of {sum(counts.values()):,}")
        hits.append(Hit(("~" if sev == "warn" else "") + "gr_exist_agreement", span,
                        fix_of(_exist_swap(verb_tok, best)), why))

    def modifies_next(i, used):
        """A bare participle that the corpus accepts before the next noun
        ('މަސްވެރިން ހުރި ކަންބޮޑުވުންތައް'): it agrees with that noun, not the one before."""
        if toks[i] not in _EXIST_BARE or i + 1 >= len(toks) or not re.fullmatch(WORD, toks[i + 1]):
            return False
        found = _exist_counts(toks[i + 1], "rel")
        return bool(found) and found[0][used] / max(sum(found[0].values()), 1) >= 0.5

    def before_noun(i):
        """A bare participle followed by a content word, which may be the noun the
        participle really agrees with. When that noun is not in the table the
        pred hit is only a warning."""
        return (toks[i] in _EXIST_BARE and i + 1 < len(toks) and re.fullmatch(WORD, toks[i + 1])
                and toks[i + 1] not in _CLAUSE_PARTICLES)

    for i, t in enumerate(toks):
        used = _exist_class(t)
        # Infinitives and verbal nouns in -ން (ހުންނަން, ތިއްބަވަން, ހުރުން) are mostly
        # purposive ('ވަގުތެއް ތިއްބަވަން', a time to stay): the noun before is not
        # their subject. Not checked.
        if not used or t.endswith("ން"):
            continue
        if i > 0 and not modifies_next(i, used):
            p = toks[i - 1]
            if (len(p) >= 4 and re.fullmatch(WORD, p) and not _exist_class(p)
                    and (p in human or not p.endswith(_EXIST_OBLIQUE))):
                n_before = len(hits)
                judge(p, t, used, "pred", f"{p} {t}", lambda v, p=p: f"{p} {v}" if v else "")
                if len(hits) > n_before and before_noun(i) and not hits[-1].rule.startswith("~"):
                    hits[-1].rule = "~" + hits[-1].rule
                    hits[-1].why += f" (warning only: '{t}' may agree with the following '{toks[i + 1]}')"
        # Relative 'ހުރި X': only when nothing before the participle can be its
        # subject (start of clause, punctuation, or a locative/dative/comitative
        # word: 'ސިންކުގައި ހުރި ...'). In 'ކެޕޭސިޓީ ހުރި ރަށެއް' ('an island
        # with capacity') ހުރި agrees with ކެޕޭސިޓީ, not with ރަށެއް.
        prev = toks[i - 1] if i > 0 else "."
        if (t in _EXIST_BARE and i + 1 < len(toks)
                and (not re.fullmatch(WORD, prev) or prev.endswith(_REL_OPENERS))
                and prev not in human):
            n = toks[i + 1]
            if len(n) >= 4 and re.fullmatch(WORD, n) and not _exist_class(n):
                judge(n, t, used, "rel", f"{t} {n}", lambda v, n=n: f"{v} {n}" if v else "")
    return hits


def grammar_check(text: str) -> list[Hit]:
    """Grammar errors an LLM typically makes, each backed by corpus counts.

    Data and evidence: rules/grammar_rules.json, guides/grammar.md.
    """
    hits = exist_check(text)
    hits += [Hit(rule, m.group(0), m.expand(rep) if rep else "", why)
             for rule, rx, rep, why in _grammar_rx() for m in rx.finditer(text)]
    return hits


def check(text: str, context: str | None = None, grammar: bool | None = None) -> list[Hit]:
    """Every violation found, as (rule id, the offending text).

    `context` adds the register rules for that kind of text; None (the default)
    checks spelling and word division only. `grammar` adds the grammar rules
    (rules/grammar_rules.json); by default they run whenever a context is
    given, so a context-free call behaves exactly as before.
    """
    if grammar is None:
        grammar = bool(context)
    text = T.normalise(text)
    hits = [Hit(rule, m.group(0)) for rule, rx in _RE.items() for m in rx.finditer(text)]

    toks = re.findall(rf"{WORD}|\S", text)
    words = radheef_words()
    for a, b in zip(toks, toks[1:]):
        if a != b or not re.fullmatch(WORD, a) or len(a) < 2:
            continue
        # §1(ކ) §2(ނ) §3(ށ) a word repeated for plurality or intensity is one
        # word -- but only when the joined form is attested. "ރައީސް ރައީސް" in
        # a sitting record is a speaker repeating himself, and joining it would
        # manufacture a non-word; that is a duplicate, reported apart.
        if a + b in words or a + b in attested_joined():
            hits.append(Hit("1k_reduplication_split", f"{a} {b}"))
        else:
            hits.append(Hit("~duplicate_word", f"{a} {b}"))
    for t in toks:
        if not re.fullmatch(WORD, t):
            continue
        # §6(ށ) a non-attaching particle glued to the word before it. A joined
        # form Radheef lists as one word (އެއްވެސް, ކޮންމެވެސް) is not an error.
        for p in NON_ATTACHING:
            stem = t[: -len(p)]
            if t.endswith(p) and len(stem) >= 2 and t not in words and p != t:
                if p == "ވެސް" and stem.endswith("ނަމަ"):
                    continue                     # counted once, as ނަމަވެސް
                hits.append(Hit("6sh_particle_joined", t))
                break
        # Thikijehi. Softer than word division, and never folded into its
        # counts: the Academy's own 2024 books still write ޤާނޫނު, ޚާއްޞަ, ޤައުމީ
        # dotted, so outside the words the thikijehi book names, "plain is
        # preferred" is the standard's direction, not settled practice.
        if not _REDUCIBLE & set(t):
            continue
        stem_hit = next((s for s in stems(t) if plain_preferred(s)), None)
        if stem_hit and stem_hit in named_examples():
            hits.append(Hit("thikijehi_named_example", t))       # the book names it
        elif stem_hit:
            hits.append(Hit("~thikijehi_radheef_plain", t))      # Radheef has it plain
        elif reducible_dotted(t):
            hits.append(Hit("~thikijehi_probably_plain", t))     # could be a name
    if context:
        hits += register_check(text, context)
    if grammar:
        hits += grammar_check(text)
    return hits


def texts_of(obj: dict, field: str) -> list[str]:
    v = obj.get(field)
    if isinstance(v, str):
        return [v]
    if isinstance(v, list):          # chat messages: judge the assistant side
        return [m["content"] for m in v if isinstance(m, dict) and m.get("role") == "assistant"]
    return []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?")
    ap.add_argument("--file", type=Path)
    ap.add_argument("--field", default="text")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--context", choices=sorted(register_rules()["contexts"]),
                    help="also check register/word choice for this kind of text "
                         "(implies --grammar)")
    ap.add_argument("--grammar", action="store_true",
                    help="also check grammar (rules/grammar_rules.json) without a context")
    args = ap.parse_args()
    grammar = True if args.grammar else None
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if args.text:
        for h in check(args.text, args.context, grammar):
            print(f"{h.rule:<28} {h.span}" + (f"  ->  {h.fix}" if h.fix else ""))
        return
    per_rule, examples = Counter(), {}
    n_docs = n_bad = n_words = 0
    with args.file.open(encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if args.limit and i >= args.limit:
                break
            for text in texts_of(json.loads(line), args.field):
                n_docs += 1
                n_words += len(T.words(text))
                hits = check(text, args.context, grammar)
                n_bad += bool(hits)
                for h in hits:
                    per_rule[h.rule] += 1
                    examples.setdefault(h.rule, h.span)
    print(f"{args.file.name}: {n_docs:,} texts, {n_words:,} words, "
          f"{n_bad:,} with a violation ({n_bad / max(n_docs, 1):.1%})")
    for rule, c in per_rule.most_common():
        print(f"  {rule:<28} {c:>8,}  ({c / max(n_words, 1) * 1000:.2f}/1k words)  e.g. {examples[rule]!r}")


if __name__ == "__main__":
    main()
