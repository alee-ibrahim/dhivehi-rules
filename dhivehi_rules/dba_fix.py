"""
Rewrite Dhivehi toward the Dhivehi Academy standard -- the parts that are safe.

The target is the official standard: Dhivehi written the way the Academy
prescribes, avoiding dotted (thikijehi) letters wherever that can be done
without harm. `dhivehi_rules.dba_rules` detects; this corrects, and only for rules whose
detection held up in a random audit of real text:

    §6(ށ) a non-attaching particle glued on      އަބަދުވެސް    -> އަބަދު ވެސް   (30/30)
    §5(ނ) an ordinal split from its number       2021 ވަނަ    -> 2021ވަނަ     (30/30)
    §6(ނ),(ރ) a plural/question particle apart    ލޯނު ތަކަށް  -> ލޯނުތަކަށް    (29/30)
    §6(ނ) a case suffix apart, joined form common  ގާނޫނު ގެ    -> ގާނޫނުގެ
    thikijehi, plain where possible               ޤާނޫނު        -> ގާނޫނު

Left alone on purpose: reduplication and negation (their detection was 19/30
and 6/30 -- "ތިރީސް ހާސް ހާސް" is a typo, ނޫ is "blue"), and punctuation,
which has not been audited.

Thikijehi is reduced only with evidence, and never for what the standard keeps
dotted:
  * reduce when Radheef or the thikijehi book has the plain form, or when the
    plain spelling is genuinely in use (>=50 corpus occurrences and >=25% as
    common as the dotted one -- which keeps ތަޢާލާ, written plain 8% of the time)
  * never: ޚ ޣ ޝ (rule 3, not in the fold at all), homographs, Hijri months,
    titles, Allah's names, anything containing ﷲ, personal names
    (rules/protected_names.json, found by where they appear -- after a title,
    in a Majlis speaker line), and any dotted word sitting next to a title or a
    name, which covers the second name of a chain the list missed.

    python -m dhivehi_rules.dba_fix "ޢިއްޒަތްތެރި ރައީސް މުޙައްމަދު މުޢިއްޒު 2021 ވަނަ އަހަރުވެސް"
"""
from __future__ import annotations

import json
import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent      # repo root: rules/, lexicon/
if __package__ in (None, ""):                       # run as a plain script
    sys.path.insert(0, str(ROOT))
from dhivehi_rules import thaana as T  # noqa: E402
from dhivehi_rules.dba_rules import (_FOLD, _RE as _RE_RULES, _REDUCIBLE, JOIN_AFTER,  # noqa: E402
                       NON_ATTACHING, NUMBER_WORDS, exception_words, plain_preferred,
                       radheef_words, stems)

TH = "ހ-޿"
TITLES = {"ރައީސް", "ޑރ.", "ޑރ", "އަލްފާޟިލް", "އަލްފާޟިލާ", "ވަޒީރު", "މެންބަރު", "މިނިސްޓަރު",
          "ފަނޑިޔާރު", "ޝައިޚު", "ޝެއިޚް", "ޝައިޚް", "އަލްއުސްތާޛު", "މަނިކުފާނު", "ބޭފުޅާ",
          "ބިން", "ބިންތު", "އިބްނު", "ކޮމިޝަނަރު", "ނައިބު", "ސުލްޠާން", "ސުލްތާން", "ކެޕްޓަން"}

_ORDINAL = re.compile(rf"(\d+|(?<![{TH}])(?:{'|'.join(NUMBER_WORDS)}))[ \t]+(ވަނަ)(?![{TH}])")
_PARTICLE_APART = re.compile(rf"(?<=[{TH}])[ \t]+((?:{'|'.join(JOIN_AFTER)})(?![{TH}]))")
_TOKEN = re.compile(rf"[{TH}]+")
_SPACE_BEFORE_STOP = re.compile(rf"(?<=[{TH}])[ \t]+\.(?![\d.])")
_NO_SPACE_AFTER_STOP = _RE_RULES["7h_no_space_after_stop"]
_PAD_OPEN = re.compile(rf"\([ \t]+(?=[{TH}])")
_PAD_CLOSE = re.compile(rf"(?<=[{TH}.])[ \t]+\)")
# §6(ނ) a case suffix written apart from its noun: "ގާނޫނު ގެ", "އެމްޑީޕީ ގައި".
# ގެ is also "house" and ގައި "body" ("އޭނާ އުޅޭ ގެ", "އޭނަގެ ގައި"), so a pair
# is joined only when the joined word is itself common in human text -- nobody
# writes "އުޅޭގެ" -- and never after a determiner ("އެ ގެ" is "that house").
_CASE_APART = re.compile(rf"(?<![{TH}])([{TH}]+)[ \t]+(ގެތެރެއިން|ގެދަށުން|ގެމަތިން|ގެފަރާތުން|ގެ|ގައި)(?![{TH}])")
_DETERMINERS = {"އެ", "މި", "ތި", "އެއް", "ހުރިހާ", "އާ", "ބޮޑު", "ކުޑަ", "ބޭރު", "އެއްވެސް",
                "ކޮން", "ކޮންމެ", "ތިން", "ދެ", "އޭނާގެ", "އޭނަގެ", "މަގޭ", "ތިބާގެ",
                # adjectives: "ރަސްމީ ގެ" is the official residence, "އަމިއްލަ ގެ" one's own house
                "ރަސްމީ", "އަމިއްލަ", "ހުސް", "ރީތި", "ބާ", "ފުރަތަމަ", "ފަހު", "ކުރީގެ"}
# "ގެ އަށް", "ގެ އިން": a detached ending after ގެ means ގެ is the noun (house).
_HOUSE_NEXT = re.compile(rf"[ \t]+(?:އަށް|އިން|ގައި|އާ|ތައް|ތަކުގެ|ތަކަށް|ދޮރު)(?![{TH}])")
CASE_JOIN_MIN = 20


@lru_cache(maxsize=1)
def names() -> frozenset[str]:
    p = ROOT / "rules" / "protected_names.json"
    return frozenset(json.loads(p.read_text(encoding="utf-8"))) if p.exists() else frozenset()


@lru_cache(maxsize=1)
def corpus_counts() -> dict[str, int]:
    out = {}
    p = ROOT / "lexicon" / "corpus_vocab.tsv"
    if p.exists():
        for line in p.open(encoding="utf-8"):
            w, _, c = line.rstrip("\n").partition("\t")
            out[w] = int(c or 0)
    return out


# Stems that keep their dots in every form, found by auditing real corrections:
#   sacred terms -- the Academy's own 2024 book writes "ކީރިތި ޤުރުއާނާ ބެހޭ ގައުމީ
#   މަރުކަޒު", the Quran dotted beside a plain ގައުމީ;
#   Arabic titles, rule 4(ނ) (ވަލީއަޙުދު, like its ޤާޟީ, ޢާމިލު, މުޙާމީ).
KEEP_PREFIXES = ("ޤުރުއާނ", "ޤުރުއާން", "ޤުރްއާނ", "ޤުރްއާން", "ޤުރުއާން", "ޙަދީޘ", "ޙަދީސ",
                 "ޞަލަވާތ", "ސުބްޙާނ", "ޞައްލަ", "ޢަލައިހި", "ރަޟިޔަ", "ވަލީއަޙުދ",
                 "ޤާޟީ", "ޢާމިލ", "މުޙާމީ")


@lru_cache(maxsize=1)
def _homograph_stems() -> tuple[str, ...]:
    """ޢަމަލު -> ޢަމަލ: a homograph keeps its dots in its derived forms too
    (ޢަމަލީ, ޢަމަލުކުރުން), not only as the bare word."""
    from dhivehi_rules.dba_rules import homographs
    return tuple(h[:-1] if h.endswith(("ު", "ި")) else h for h in homographs() if len(h) >= 3)


@lru_cache(maxsize=1)
def _name_stems() -> frozenset[str]:
    """ޢިމްރާން -> ޢިމްރާ: a name changes its ending when inflected (ޢިމްރާނަކީ,
    ޢިމްރާނުގެ), so it is protected by its stem, not only its citation form. The
    eval-reference audit caught ޢިމްރާނަކީ being folded without this. Erring on
    the side of protection only ever costs a reduction, never corrupts a word."""
    # The stem follows how a name inflects, so it stays as specific as possible:
    # -ން becomes -ނ (ޢިމްރާން -> ޢިމްރާނަކީ); a final short vowel or sukun drops
    # but the consonant stays (ޙަމަދު -> ޙަމަދަށް -- so ޙަމަލާ "attack" is not
    # mistaken for it); a long vowel is kept whole (ޢަލީ -> ޢަލީގެ).
    out = set()
    for n in names():
        n = n.rstrip(".")
        if n.endswith("ން"):
            base = n[:-2] + "ނ"
        elif n.endswith(("ު", "ި", "ަ", "ް")):
            base = n[:-1]
        else:
            base = n
        if len(base) >= 3:
            out.add(base)
    return frozenset(out)


def _protected(word: str) -> bool:
    if (word in exception_words() or word in names() or "ﷲ" in word
            or word.rstrip(".") in names()
            or word.startswith(KEEP_PREFIXES) or word.startswith(_homograph_stems())):
        return True
    stems_ = _name_stems()
    return any(word[:k] in stems_ for k in range(3, len(word) + 1))


@lru_cache(maxsize=200_000)
def plain_form(word: str) -> str | None:
    """The plain spelling to write instead of this dotted word, or None to keep it."""
    if not (_REDUCIBLE & set(word)) or _protected(word):
        return None
    folded = word.translate(_FOLD)
    if any(plain_preferred(s) for s in stems(word)):
        return folded                                   # Radheef / the book say plain
    counts = corpus_counts()
    for s in stems(word):
        if not (_REDUCIBLE & set(s)) or _protected(s):
            continue
        plain = counts.get(s.translate(_FOLD), 0)
        if plain >= 50 and plain >= 0.25 * max(counts.get(s, 0), 1):
            return folded                               # people write it plain
    return None


def _split_particle(tok: str) -> str:
    """§6(ށ): write a glued non-attaching particle apart -- unless Radheef has the
    joined form as one word (އެއްވެސް, އަދިވެސް, އެހެންނަމަވެސް)."""
    if tok in radheef_words():
        return tok
    for p in NON_ATTACHING:                              # longest first: ނަމަވެސް before ވެސް
        stem = tok[: -len(p)]
        if tok.endswith(p) and len(stem) >= 2 and tok != p:
            return f"{_split_particle(stem)} {p}"
    return tok


def fix(text: str) -> tuple[str, list[tuple[str, str, str]]]:
    """(corrected text, [(rule, before, after), ...])."""
    changes: list[tuple[str, str, str]] = []
    text = T.normalise(text)

    # §7(ހ),(ނ) punctuation spacing, audited 25/25 each on real text. Order
    # matters: the space before a stop goes first, so "ކުރައްވަމުން .މިފަދަ"
    # ends as "ކުރައްވަމުން. މިފަދަ". Brackets only around Thaana -- the English
    # side of the parallel data is PTB-tokenised ("( 1844 )") and is not ours.
    def punct(rule, rx, repl):
        nonlocal text
        def sub(m):
            new = repl(m)
            changes.append((rule, m.group(0), new))
            return new
        text = rx.sub(sub, text)
    punct("7h_space_before_stop", _SPACE_BEFORE_STOP, lambda m: ".")
    punct("7h_no_space_after_stop", _NO_SPACE_AFTER_STOP, lambda m: m.group(0) + " ")
    punct("7n_padded_bracket", _PAD_OPEN, lambda m: "(")
    punct("7n_padded_bracket", _PAD_CLOSE, lambda m: ")")

    def ordinal(m):
        changes.append(("5n_ordinal", m.group(0), m.group(1) + m.group(2)))
        return m.group(1) + m.group(2)
    text = _ORDINAL.sub(ordinal, text)

    def particle(m):
        changes.append(("6n_particle", m.group(0), m.group(1)))
        return m.group(1)
    text = _PARTICLE_APART.sub(particle, text)

    def case(m):
        noun, suf = m.group(1), m.group(2)
        joined = noun + suf
        if noun in _DETERMINERS or corpus_counts().get(joined, 0) < CASE_JOIN_MIN:
            return m.group(0)
        if suf == "ގެ" and _HOUSE_NEXT.match(m.string, m.end()):
            return m.group(0)
        changes.append(("6n_case_suffix", m.group(0), joined))
        return joined
    text = _CASE_APART.sub(case, text)

    toks = [(m.start(), m.end(), m.group(0)) for m in _TOKEN.finditer(text)]
    out, last = [], 0
    for i, (a, b, tok) in enumerate(toks):
        new = _split_particle(tok)
        if new != tok:
            changes.append(("6sh_particle", tok, new))
        # A dotted word beside a title or a name is taken to be part of a name.
        prev_tok = toks[i - 1][2] if i else ""
        next_tok = toks[i + 1][2] if i + 1 < len(toks) else ""
        context_name = prev_tok in TITLES or prev_tok in names() or next_tok in names()
        if not context_name:
            parts = new.split(" ")
            folded = [plain_form(p) or p for p in parts]
            if folded != parts:
                changes.append(("thikijehi", new, " ".join(folded)))
                new = " ".join(folded)
        out.append(text[last:a])
        out.append(new)
        last = b
    out.append(text[last:])
    return "".join(out), changes


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    text = " ".join(sys.argv[1:])
    fixed, changes = fix(text)
    print(fixed)
    for rule, a, b in changes:
        print(f"  {rule:<14} {a!r} -> {b!r}")


if __name__ == "__main__":
    main()
