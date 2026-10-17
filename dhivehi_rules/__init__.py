"""Canonical Dhivehi writing rules: Thaana validation, Dhivehi Academy (DBA)
spelling and word division, register and grammar checks, the official 1977
Latin romanisation, and the pre-TTS script gate.

Data is read from the repository's rules/ and lexicon/ directories (located
relative to this package), so install with ``pip install -e``.

    from dhivehi_rules import thaana, dba_rules, dba_fix, script_gate, thaana_latin
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"
LEXICON_DIR = ROOT / "lexicon"
GUIDES_DIR = ROOT / "guides"

__version__ = "0.1.0"
__all__ = ["ROOT", "RULES_DIR", "LEXICON_DIR", "GUIDES_DIR", "__version__"]
