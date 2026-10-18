"""Parse official answer-key PDFs into data/keys/<id>.json by matching word positions.

Each answer is a list of accepted answers: usually one letter, sometimes two ("C or D"),
and occasionally a free-response value (e.g. "3:21:49").
Usage: python3 pipeline/parse_keys.py
"""
import json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def words(pdf):
    html = subprocess.run(["pdftotext", "-bbox", "-f", "1", "-l", "1", pdf, "-"],
                          capture_output=True, text=True, check=True).stdout
    pat = r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>'
    return [(float(a), float(b), float(c), float(d), w) for a, b, c, d, w in re.findall(pat, html)]


def parse(pdf):
    ws = words(pdf)
    nums = {int(w): (x0, (y0 + y1) / 2, x1) for x0, y0, x1, y1, w in ws
            if w.isdigit() and 1 <= int(w) <= 20 and x0 < 120}
    if len(nums) != 20:
        raise ValueError(f"found {len(nums)} question numbers")
    col_l = max(v[2] for v in nums.values())
    letters = [(x0, (y0 + y1) / 2, w) for x0, y0, x1, y1, w in ws
               if col_l < x0 < col_l + 160]
    # rows are ~equal height; assign each letter to the nearest question row
    answers = {n: [] for n in nums}
    for x, y, w in sorted(letters):
        n = min(nums, key=lambda k: abs(nums[k][1] - y))
        if abs(nums[n][1] - y) < 12 and w != "or":
            answers[n].append(w)
    return {str(n): answers[n] for n in sorted(answers)}


def main():
    out = DATA / "keys"
    out.mkdir(exist_ok=True)
    for exam in json.loads((ROOT / "pipeline" / "sources.json").read_text())["exams"]:
        key = parse(DATA / "raw" / exam["id"] / "key.pdf")
        bad = [n for n, a in key.items() if not a]
        (out / f"{exam['id']}.json").write_text(json.dumps(key, indent=1))
        print(exam["id"], " ".join("/".join(a) or "?" for a in key.values()), "MISSING " + str(bad) if bad else "")


if __name__ == "__main__":
    main()
