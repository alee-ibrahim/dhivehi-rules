"""
Thaana -> Latin by the official romanisation rules of 23 May 1977
(ދިވެހިބަސް އިނގިރޭސި (ލެޓިން) އަކުރުން ލިޔުމުގެ ޤަވާޢިދު; see SOURCES.md).

These are the rules behind official Latin-script Dhivehi -- names in documents,
the 1980 law printed in Latin at the end of the same booklet. They are not how
people type Dhivehi in Latin today (that is the informal romanisation the
`translit` task already covers), which is exactly why the model should read
both.

    §1 consonants    ހ h  ށ sh  ނ n  ރ r  ބ b  ޅ lh  ކ k  ވ v  މ m  ފ f  ދ dh  ތ th
                     ލ l  ގ g  ޏ gn  ސ s  ޑ d  ޒ z  ޓ t  ޔ y  ޕ p  ޖ j  ޗ ch
    §2 Arabic        ޞ s'  ޟ l'  ޠ t'  ޡ z'  ޥ w  ޘ th'  ޙ h'  ޚ kh  ޛ dh'  ޣ gh  ޤ q
                     ޝ: the table gives sh', but the booklet's own ނިޝާން is "nishaan" --
                     ޝ as a Dhivehi sound, as the 2024 thikijehi rules also treat it
                     ޢ = the vowel with an apostrophe: a'mal, i'shq, Maso'odh
    §3 vowels        ަ a  ާ aa  ި i  ީ ee  ު u  ޫ oo  ެ e  ޭ ey  ޮ o  ޯ oa ; އ + vowel = the vowel
    §4 sukun         final އް -> h (meeheh), ން -> n (fen), ށް -> iy (foiy), ސް -> s (gas);
                     before a consonant: that consonant, doubled after އް (bappa, bayyeh),
                     ން before މ -> m (mamma)
    §5               a bare ނ before a consonant -> n' (kan'di, an'bu)
    §6               a sentence begins with a capital

Not automated, and so never relied on: §6's capitals for proper nouns (Thaana
has no case to carry them) and §8's rule that English words keep English
spelling (ޓިކެޓް is "ticket", not "tiket") -- a word-level judgement this file
cannot make.

    python -m dhivehi_rules.thaana_latin "ބައްޕަ މާދަމާ ރަށަށް އަންނާނެއެވެ."
    python -m dhivehi_rules.thaana_latin --test
"""
from __future__ import annotations

import re
import sys

CONS = {
    "ހ": "h", "ށ": "sh", "ނ": "n", "ރ": "r", "ބ": "b", "ޅ": "lh", "ކ": "k", "އ": "",
    "ވ": "v", "މ": "m", "ފ": "f", "ދ": "dh", "ތ": "th", "ލ": "l", "ގ": "g", "ޏ": "gn",
    "ސ": "s", "ޑ": "d", "ޒ": "z", "ޓ": "t", "ޔ": "y", "ޕ": "p", "ޖ": "j", "ޗ": "ch",
    "ޞ": "s'", "ޟ": "l'", "ޠ": "t'", "ޡ": "z'", "ޥ": "w", "ޘ": "th'", "ޙ": "h'",
    "ޚ": "kh", "ޛ": "dh'", "ޝ": "sh", "ޣ": "gh", "ޤ": "q", "ޜ": "zh", "ޢ": "",
}
VOWEL = {"ަ": "a", "ާ": "aa", "ި": "i", "ީ": "ee", "ު": "u", "ޫ": "oo",
         "ެ": "e", "ޭ": "ey", "ޮ": "o", "ޯ": "oa"}
SUKUN = "ް"
_LONG = {"aa", "ee", "oo", "ey", "oa"}
PUNCT = {"،": ",", "؟": "?", "؛": ";"}


def _word(w: str) -> str:
    out: list[str] = []
    i, n = 0, len(w)
    while i < n:
        c = w[i]
        nxt = w[i + 1] if i + 1 < n else ""
        if c in VOWEL or c == SUKUN:            # stray mark: nothing to attach it to
            i += 1
            continue
        if c not in CONS:
            out.append(PUNCT.get(c, c))
            i += 1
            continue
        if nxt in VOWEL:
            v = VOWEL[nxt]
            if c == "ޢ":                        # §2: a'mal, i'shq, Maso'odh, a'ailaa
                out.append(v[0] + "'" + v[1:] if v in _LONG else v + "'")
            else:
                out.append(CONS[c] + v)
            i += 2
            continue
        if nxt == SUKUN:
            after = w[i + 2] if i + 2 < n else ""
            final = after == "" or after not in CONS
            if c == "އ":
                if final:
                    out.append("h")                       # §4: meeheh
                elif after in CONS and CONS[after]:
                    out.append(CONS[after])               # §4: bappa, bayyeh
            elif c == "ށ" and final:
                out.append("iy")                          # §4: foiy, baiy
            elif c == "ނ" and after == "މ":
                out.append("m")                           # §4: mamma
            else:
                out.append(CONS[c])                       # fen, gas, ramzu, milku
            i += 2
            continue
        if c == "ނ" and nxt in CONS:                      # §5: prenasalised stop
            out.append("n'")
            i += 1
            continue
        out.append(CONS[c])                               # bare letter: an abbreviation
        i += 1
    return "".join(out)


def romanise(text: str) -> str:
    """Official 1977 romanisation of a Thaana text; sentences start with a capital."""
    parts = re.split(r"(\s+)", text)
    out = "".join(_word(p) if p.strip() else p for p in parts)
    # §6: a capital at the start of each sentence.
    return re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), out)


# The booklet's own examples (§3-§5), Thaana as printed beside each one.
BOOK_EXAMPLES = {
    "އަންނާރު": "annaaru", "އަލަމާރި": "alamaari", "އިރު": "iru", "އިސްކުރު": "iskuru",
    "އެދުރު": "edhuru", "އެތެރެ": "ethere", "އުރަ": "ura", "އުތުރު": "uthuru",
    "އޮޑާ": "odaa", "އޮނު": "onu", "ނަލަ": "nala", "ހަމަ": "hama", "ބާރު": "baaru",
    "ނާރު": "naaru", "ނިޝާން": "nishaan", "ފިލި": "fili", "ރީތި": "reethi", "ބީރު": "beeru",
    "ހުތުރު": "huthuru", "ސުތުލި": "suthuli", "ކޫރު": "kooru", "ތޫނު": "thoonu",
    "ބެރެބެދި": "berebedhi", "ފެރިދޫ": "feridhoo", "ފޭރު": "feyru", "ބޭބެ": "beybe",
    "ބޮކަރު": "bokaru", "ފޮނު": "fonu", "ރޯނު": "roanu", "ސޯނާ": "soanaa", "ފައި": "fai",
    "ސައި": "sai", "އަތަރު": "atharu", "އާރު": "aaru", "އިސްތިރި": "isthiri", "ރައީސް": "raees",
    "އީޓު": "eetu", "ފައުނު": "faunu", "އުކުނު": "ukunu", "އޫރު": "ooru", "ބައެއް": "baeh",
    "އެކަތަ": "ekatha", "އޭދަފުށި": "eydhafushi", "އޭނާ": "eynaa", "އޮޅު": "olhu",
    "އޯބު": "oabu", "އައިބު": "aibu", "އައިނު": "ainu", "ކޮއިމަލާ": "koimalaa",
    "މުނިއަވަސް": "muniavas", "މީހެއް": "meeheh", "ތުން": "thun", "ފެން": "fen",
    "ބަށް": "baiy", "ކެށް": "keiy", "ގާށް": "gaaiy", "މުށް": "muiy", "އޯށް": "oaiy",
    "ފޮށް": "foiy", "ގަސް": "gas", "ވިސްނުން": "visnun", "ރަމްޒު": "ramzu", "މިލްކު": "milku",
    "މަންމަ": "mamma", "ބައްޕަ": "bappa", "ބައްޔެއް": "bayyeh", "ކަނޑި": "kan'di",
    "އަނބު": "an'bu",
}


def _test() -> int:
    bad = [(t, want, _word(t)) for t, want in BOOK_EXAMPLES.items() if _word(t) != want]
    for t, want, got in bad:
        print(f"  MISMATCH {t}: book {want!r}, got {got!r}")
    print(f"{len(BOOK_EXAMPLES) - len(bad)}/{len(BOOK_EXAMPLES)} booklet examples reproduced")
    return 1 if bad else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1:] == ["--test"]:
        sys.exit(_test())
    print(romanise(" ".join(sys.argv[1:])))
