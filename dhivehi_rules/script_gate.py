"""
The one gate every Dhivehi script passes through before it reaches TTS.

    No Dhivehi text goes to TTS without passing script_gate.py.

It runs, in order:

  1. thaana.validate       well-formed Thaana: every consonant has a fili or a
                           sukun, no orphan or doubled marks, no stray Indic script
  2. dba_rules.check       Dhivehi Academy spelling and word division
  3. register rules        word choice for viewers (rules/register_rules.json)
  4. grammar rules         noun/verb agreement and other LLM-typical errors, each
                           backed by corpus counts (rules/grammar_rules.json)

Errors block. Warnings (rule ids with a leading ~) are printed and allowed; a
native speaker should look at them.

From Python:

    from dhivehi_rules.script_gate import check_script, gate, gate_lines
    ok, report = check_script(text, "video")          # never raises
    gate(text, label="h", context="ad")               # SystemExit(2) on errors
    gate_lines(lines_dict, context="ad", force=False) # all lines, one report

From the shell (exit 0 = clean or warnings only, 2 = errors, 1 = bad usage):

    python -m dhivehi_rules.script_gate --context ad "ސުވާލެއް އޮތް ނަމަ، ގުޅުއްވާ."
    python -m dhivehi_rules.script_gate --context ad --file vo/lines.json   # JSON {key: line}
    python -m dhivehi_rules.script_gate --context presenter --file script.md  # one line per Thaana line

`force=True` (or --force) lets a blocked script through. It prints a loud
banner to stderr and appends the text and the errors to
logs/gate_overrides.log, so every override leaves a record.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent      # repo root: rules/, lexicon/
if __package__ in (None, ""):                       # run as a plain script
    sys.path.insert(0, str(ROOT))
from dhivehi_rules import dba_rules as D  # noqa: E402
from dhivehi_rules import thaana as T  # noqa: E402

CONTEXTS = tuple(sorted(D.register_rules()["contexts"]))
OVERRIDE_LOG = ROOT / "logs" / "gate_overrides.log"
_TH = re.compile("[\u0780-\u07bf]")


def check_script(text: str, context: str = "video") -> tuple[bool, str]:
    """(ok, report). ok is False if there is any error. The report lists every
    finding, one per line: ERROR/warn, rule id, the offending text, the
    suggested fix and the reason."""
    if context not in CONTEXTS:
        raise ValueError(f"unknown context {context!r}; one of {CONTEXTS}")
    lines, n_err = [], 0
    norm = T.normalise(text)
    r = T.validate(norm)
    for name in ("bare_consonant", "orphan_mark", "double_mark"):
        if getattr(r, name):
            n_err += 1
            words = [w for w in re.findall(r"\S+", norm)
                     if getattr(T.validate(w.strip(".,!?؟،:;\"'()")), name)]
            lines.append(f"ERROR thaana_{name} x{getattr(r, name)}: "
                         f"«{' '.join(words)}» (malformed Thaana: every consonant needs a fili "
                         "or sukun, e.g. ސިލްވަރ -> ސިލްވަރު)")
    if r.foreign:
        n_err += 1
        lines.append(f"ERROR thaana_foreign_script {r.foreign} (non-Thaana script in the text)")
    for h in D.check(text, context, grammar=True):
        warn = h.rule.startswith("~")
        n_err += not warn
        line = f"{'warn ' if warn else 'ERROR'} {h.rule.lstrip('~')}: «{h.span}»"
        if h.fix:
            line += f" -> «{h.fix}»"
        if h.why:
            line += f"   [{h.why}]"
        lines.append(line)
    return n_err == 0, "\n".join(lines) if lines else "clean"


def _log_override(label: str, text: str, report: str) -> None:
    OVERRIDE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with OVERRIDE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"{_dt.datetime.now().isoformat(timespec='seconds')}\t{label}\t{sys.argv[0]}\n"
                 f"  text: {text}\n" + "".join(f"  {l}\n" for l in report.splitlines()))


def _banner(msg: str) -> None:
    bar = "!" * 78
    print(f"\n{bar}\n!! {msg}\n{bar}\n", file=sys.stderr, flush=True)


def gate_lines(lines: dict[str, str], context: str = "video", force: bool = False,
               label: str = "") -> None:
    """Check every line, print one report, and stop (SystemExit 2) if any has
    an error, unless force=True, which logs the override loudly and continues."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    bad = {}
    for k, text in lines.items():
        if not _TH.search(text or ""):
            continue                      # no Dhivehi in this line (an English label, a number)
        ok, report = check_script(text, context)
        tag = f"{label}/{k}" if label else k
        if report != "clean":
            print(f"[script_gate {tag}] {text}\n" + "".join(f"    {l}\n" for l in report.splitlines()),
                  end="", flush=True)
        if not ok:
            bad[tag] = (text, report)
    n = len(lines)
    if not bad:
        print(f"[script_gate] {n} line(s) passed (context={context}).", flush=True)
        return
    if force:
        _banner(f"script_gate: --force used. {len(bad)} line(s) with Dhivehi ERRORS are going to "
                f"TTS anyway: {', '.join(bad)}. Logged to {OVERRIDE_LOG}")
        for tag, (text, report) in bad.items():
            _log_override(tag, text, report)
        return
    _banner(f"script_gate: BLOCKED. {len(bad)} of {n} line(s) have Dhivehi errors: "
            f"{', '.join(bad)}. Nothing was sent to TTS.")
    print("Fix each ERROR above (the suggested form follows ->) and run again.\n"
          "Override only if a native speaker has checked the line: re-run with --force.",
          file=sys.stderr, flush=True)
    raise SystemExit(2)


def gate(text: str, label: str = "", context: str = "video", force: bool = False) -> None:
    """gate_lines for a single string."""
    gate_lines({label or "text": text}, context, force)


def lines_of(path: Path) -> dict[str, str]:
    """{key: line} from a lines.json ({key: text} or [text, ...]) or from a text/markdown
    file (every line that contains Thaana, keyed by line number)."""
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return {str(k): v for k, v in obj.items() if isinstance(v, str)}
        return {str(i): v for i, v in enumerate(obj) if isinstance(v, str)}
    return {f"L{i}": l.strip() for i, l in enumerate(raw.splitlines(), 1) if _TH.search(l)}


def main() -> None:
    ap = argparse.ArgumentParser(description="Gate Dhivehi text before TTS.")
    ap.add_argument("text", nargs="?", help="the Dhivehi text (or use --file / stdin)")
    ap.add_argument("--file", type=Path, action="append",
                    help="lines.json, .txt or .md; may be given more than once")
    ap.add_argument("--context", choices=CONTEXTS, default="video")
    ap.add_argument("--force", action="store_true", help="let errors through (logged loudly)")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    if args.file:
        lines = {}
        for f in args.file:
            lines.update({f"{f.name}:{k}": v for k, v in lines_of(f).items()})
    elif args.text:
        lines = {"text": args.text}
    elif not sys.stdin.isatty():
        lines = {"stdin": sys.stdin.read()}
    else:
        ap.error("give the text, --file, or pipe text on stdin")
    gate_lines(lines, args.context, args.force)


if __name__ == "__main__":
    main()
