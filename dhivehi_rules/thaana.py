"""
Thaana normalisation and orthographic validation. Standard library only.

Thaana is an abugida: every consonant carries exactly one vowel sign (fili) or
a sukun marking the absence of a vowel. That rule is mechanical, which makes a
large class of spelling errors detectable without knowing any Dhivehi -- a bare
consonant, an orphaned fili, or a doubled fili is wrong no matter what the word
was meant to be.

This module is the quality backbone of the corpus pipeline. Everything
downstream trusts it, so it is deliberately dependency-free and heavily
commented.

Unicode block U+0780-U+07BF:
    U+0780-U+07A5   38 consonant letters (haa .. waavu)
    U+07A6-U+07AF   10 vowel signs (fili)
    U+07B0          sukun (no vowel)
    U+07B1          naa (rare, Arabic loans)
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field, asdict

# --- character classes ------------------------------------------------------
CONSONANTS = frozenset(range(0x0780, 0x07A6)) | {0x07B1}
FILI = frozenset(range(0x07A6, 0x07B0))          # 10 vowel signs
SUKUN = 0x07B0
MARKS = FILI | {SUKUN}
THAANA = CONSONANTS | MARKS

ALIFU = 0x0787          # vowel carrier
SHAVIYANI = 0x0781
NOONU = 0x0782          # prenasalisation marker -- see validate()

# Invisible characters that ruin dedup and tokenisation but render identically.
INVISIBLES = "".join(chr(c) for c in [
    0x200B, 0x200C, 0x200D,              # ZWSP, ZWNJ, ZWJ
    0x200E, 0x200F,                       # LRM, RLM
    0x202A, 0x202B, 0x202C, 0x202D, 0x202E,   # bidi embedding/override
    0x2066, 0x2067, 0x2068, 0x2069,       # bidi isolates
    0xFEFF,                               # BOM
    0x00AD,                               # soft hyphen
])

# Scripts that bleed into Dhivehi text from neighbouring languages, usually a
# sign the text came from a model or an OCR system that lost the plot.
FOREIGN_RANGES = {
    "devanagari": range(0x0900, 0x0980),
    "bengali": range(0x0980, 0x0A00),
    "tamil": range(0x0B80, 0x0C00),
    "malayalam": range(0x0D00, 0x0D80),
    "sinhala": range(0x0D80, 0x0E00),
    "burmese": range(0x1000, 0x10A0),
}

ARABIC_RANGES = [range(0x0600, 0x0700), range(0x0750, 0x0780),
                 range(0xFB50, 0xFE00), range(0xFE70, 0xFF00)]

# Arabic-Indic digits -> ASCII. Dhivehi writing uses Western digits.
_DIGIT_MAP = {**{chr(0x0660 + i): str(i) for i in range(10)},
              **{chr(0x06F0 + i): str(i) for i in range(10)}}

# Punctuation genuinely used in Dhivehi, plus variants to fold together.
_PUNCT_MAP = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "…": "...",
    " ": " ", "　": " ",
}

_WS_RE = re.compile(r"[ \t - ]+")
_NL_RE = re.compile(r"\n{3,}")
_CTRL_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")


def normalise(text: str) -> str:
    """Canonical form for storage, dedup and training.

    Idempotent: normalise(normalise(x)) == normalise(x).
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = _CTRL_RE.sub("", text)
    text = text.translate({ord(c): None for c in INVISIBLES})
    text = text.translate({ord(k): v for k, v in _DIGIT_MAP.items()})
    text = text.translate({ord(k): v for k, v in _PUNCT_MAP.items()})
    text = _WS_RE.sub(" ", text)
    text = _NL_RE.sub("\n\n", text)
    return "\n".join(line.strip() for line in text.split("\n")).strip()


@dataclass
class Report:
    """Result of validating one piece of text."""
    chars: int = 0
    thaana_chars: int = 0
    consonants: int = 0
    marks: int = 0
    latin_chars: int = 0
    arabic_chars: int = 0
    digit_chars: int = 0
    foreign: dict[str, int] = field(default_factory=dict)

    bare_consonant: int = 0     # consonant with no fili/sukun -- always wrong
    orphan_mark: int = 0        # fili with no consonant before it
    double_mark: int = 0        # two marks in a row

    @property
    def thaana_ratio(self) -> float:
        letters = self.thaana_chars + self.latin_chars + self.arabic_chars
        return self.thaana_chars / letters if letters else 0.0

    @property
    def fili_ratio(self) -> float:
        """Marks per consonant. Well-formed Dhivehi sits at 1.0."""
        return self.marks / self.consonants if self.consonants else 0.0

    @property
    def orthography_errors(self) -> int:
        return self.bare_consonant + self.orphan_mark + self.double_mark

    @property
    def error_rate(self) -> float:
        """Orthographic errors per consonant."""
        return self.orthography_errors / self.consonants if self.consonants else 0.0

    def to_dict(self) -> dict:
        d = asdict(self)
        d.update(thaana_ratio=round(self.thaana_ratio, 4),
                 fili_ratio=round(self.fili_ratio, 4),
                 orthography_errors=self.orthography_errors,
                 error_rate=round(self.error_rate, 5))
        return d


def _script_of(cp: int) -> str | None:
    for name, rng in FOREIGN_RANGES.items():
        if cp in rng:
            return name
    return None


def validate(text: str) -> Report:
    """Scan text once, counting composition and orthographic violations.

    Two constructions look like a missing fili but are correct Dhivehi, and
    both are common enough that failing to allow for them rejects a large slice
    of perfectly good text:

    1. Prenasalisation. A bare noonu before another consonant marks a
       prenasalised stop -- ދަނޑި, ކަނޑައަޅާ, ހިނގައި, ކެނޑިޑޭޓް. The noonu
       correctly carries neither fili nor sukun.
    2. Single-letter abbreviations followed by a full stop, such as the
       rufiyaa marker in "4.72ރ.".
    """
    r = Report(chars=len(text))
    n = len(text)
    prev_was_consonant = False
    prev_was_mark = False

    for i, ch in enumerate(text):
        cp = ord(ch)
        nxt = text[i + 1] if i + 1 < n else ""
        nxt_cp = ord(nxt) if nxt else -1

        if cp in CONSONANTS:
            if prev_was_consonant:
                # The PREVIOUS consonant had no mark. Allowed only if it was a
                # prenasalising noonu sitting directly before this consonant.
                if ord(text[i - 1]) != NOONU:
                    r.bare_consonant += 1
            r.consonants += 1
            r.thaana_chars += 1
            prev_was_consonant, prev_was_mark = True, False
            continue

        if cp in MARKS:
            if prev_was_mark:
                r.double_mark += 1
            elif not prev_was_consonant:
                r.orphan_mark += 1
            r.marks += 1
            r.thaana_chars += 1
            prev_was_consonant, prev_was_mark = False, True
            continue

        # Any non-Thaana character ends a syllable; an unresolved consonant
        # before it never received its fili -- unless it is an abbreviation
        # such as "ރ." where a lone letter is followed by a full stop.
        if prev_was_consonant and ch != ".":
            r.bare_consonant += 1
        prev_was_consonant = prev_was_mark = False

        if ch.isascii() and ch.isalpha():
            r.latin_chars += 1
        elif ch.isdigit():
            r.digit_chars += 1
        elif any(cp in rng for rng in ARABIC_RANGES):
            r.arabic_chars += 1
        elif (s := _script_of(cp)):
            r.foreign[s] = r.foreign.get(s, 0) + 1

    if prev_was_consonant:      # trailing consonant at end of text
        r.bare_consonant += 1
    return r


def is_dhivehi(text: str, min_ratio: float = 0.70, min_consonants: int = 5) -> bool:
    """Cheap language gate: mostly-Thaana and long enough to judge."""
    r = validate(text)
    return r.consonants >= min_consonants and r.thaana_ratio >= min_ratio


def words(text: str) -> list[str]:
    return [w for w in re.split(r"\s+", text) if w]


__all__ = ["normalise", "validate", "is_dhivehi", "words", "Report",
           "CONSONANTS", "FILI", "MARKS", "THAANA", "FOREIGN_RANGES"]
