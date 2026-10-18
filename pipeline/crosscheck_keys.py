"""Cross-check each transcribed answer key against every independent source we can parse.

Sources (each only used when it yields a complete, unambiguous answer list):
  sheet     the official key PDF's own text layer, read by word position (parse_keys.parse)
  alt<i>    the second copy of the key from the Marta Hidegkuti archive (.pdf or .doc)
  livshutz  "Answer - X" lines in Leo Livshutz's solutions, in problem order
  short     "N. X ..." lines in AMATYC's typed "Short Answers" solutions
  tex       \\TeXButton{correct answer} markers in the original 1985-1999 LaTeX

Usage: python3 pipeline/crosscheck_keys.py [exam_id ...]
Prints every disagreement not yet listed in data/review/key_disagreements.json (reviewed by eye);
exit status 1 if there are any.
"""
import re, sys

from common import DATA, load_json, sources
from parse_keys import parse

LETTER = re.compile(r"^[A-F]$")


def from_sheet(pdf, n):
    try:
        got = parse(pdf)
    except Exception:
        return None
    out = {k: v for k, v in got.items() if v and all(LETTER.match(a) for a in v)}
    return out if len(out) >= n - 3 else None  # a few rows may hold notes/values instead of letters


def from_doc_text(text, n):
    # .doc keys convert to "number" and "letter" on consecutive lines, or "n  X" on one line
    out = {}
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for i, l in enumerate(lines):
        m = re.match(r"^(\d{1,2})\s+([A-E])$", l)
        if m:
            out[m.group(1)] = [m.group(2)]
        elif re.fullmatch(r"\d{1,2}", l) and i + 1 < len(lines) and LETTER.match(lines[i + 1]):
            out.setdefault(l, [lines[i + 1]])
    out = {k: v for k, v in out.items() if 1 <= int(k) <= n}
    return out if len(out) >= n - 3 else None


def from_livshutz(text, n):
    found = re.findall(r"Answer\s*[-–—:]\s*\(?([A-E])\)?", text)
    return {str(i + 1): [a] for i, a in enumerate(found)} if len(found) == n else None


def from_short_answers(text, n):
    out = {}
    for m in re.finditer(r"^\s*(\d{1,2})\.\s+([A-E])\b", text, re.M):
        out.setdefault(m.group(1), [m.group(2)])
    return out if len(out) >= n - 2 else None


def from_tex(text, n):
    items = re.split(r"\\item\b", text)[1:]
    out = {}
    for i, item in enumerate(items[:n], start=1):
        marker = item.find("TeXButton{correct answer}")
        if marker < 0:
            continue
        labels = list(re.finditer(r"\b([A-E])\)", item[:marker]))
        if labels:
            out[str(i)] = [labels[-1].group(1)]
    return out or None


def main(ids):
    reviewed_path = DATA / "review" / "key_disagreements.json"
    reviewed = load_json(reviewed_path) if reviewed_path.exists() else {}
    disagreements = 0
    for exam_id, src in sources().items():
        if ids and exam_id not in ids:
            continue
        key_path = DATA / "keys" / f"{exam_id}.json"
        if not key_path.exists():
            continue
        key = load_json(key_path)
        ours = key["answers"]
        voided = set(map(str, key.get("voided", [])))
        n = len(ours)
        raw = DATA / "raw" / exam_id
        text = lambda kind: (DATA / "text" / exam_id / f"{kind}.txt").read_text(errors="ignore")
        checks = {}
        if (raw / "key.pdf").exists() and not src.get("key_in_exam"):
            checks["sheet"] = from_sheet(raw / "key.pdf", n)
        for i, _ in enumerate(src.get("alt_keys", [])):
            f = next(raw.glob(f"alt{i}.*"))
            checks[f"alt{i}"] = from_sheet(f, n) if f.suffix == ".pdf" else from_doc_text(text(f"alt{i}"), n)
            if checks[f"alt{i}"] is None and f.suffix == ".pdf":
                checks[f"alt{i}"] = from_doc_text(text(f"alt{i}"), n)
        for i, s in enumerate(src["solutions"]):
            t = text(f"sol{i}")
            if "Livshutz" in s["source"]:
                checks["livshutz"] = from_livshutz(t, n)
            elif s["source"].startswith("AMATYC"):
                checks[f"short{i}"] = from_short_answers(t, n)
        if (raw / "source.tex").exists():
            checks["tex"] = from_tex((raw / "source.tex").read_text(errors="ignore"), n)

        used = {k: v for k, v in checks.items() if v}
        problems = []
        for name, theirs in used.items():
            for num, ans in theirs.items():
                mine = ours.get(num, [])
                if num in voided or not mine:
                    continue
                if not set(ans) & set(mine) and f"{exam_id} #{num} {name}" not in reviewed:
                    problems.append(f"#{num}: key {mine} vs {name} {ans}")
        status = "OK" if not problems else f"{len(problems)} DISAGREEMENT(S)"
        print(f"{exam_id}: checked against {sorted(used) or 'nothing'} -> {status}")
        for p in problems:
            print("   ", p)
        disagreements += len(problems)
    sys.exit(1 if disagreements else 0)


if __name__ == "__main__":
    main(set(sys.argv[1:]))
