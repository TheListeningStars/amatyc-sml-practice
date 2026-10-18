"""Validate transcribed exams.

Usage:
  python3 pipeline/check.py <exam_id> [...]        validate exam + key JSON (schema, key match, KaTeX)
  python3 pipeline/check.py --crop <exam_id> <n>   render problem n's figure crop to data/review/crops/
                                                   so you can look at it
  python3 pipeline/check.py --all                  validate every transcribed exam
"""
import sys
from common import DATA, crop_figure, load_json, validate

args = sys.argv[1:]
if args[:1] == ["--crop"]:
    exam_id, n = args[1], int(args[2])
    p = next(p for p in load_json(DATA / "exams" / f"{exam_id}.json")["problems"] if p["n"] == n)
    out = DATA / "review" / "crops" / f"{exam_id}-{n}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    crop_figure(exam_id, p["figure"]).save(out)
    print(out)
    sys.exit()

ids = sorted(f.stem for f in (DATA / "exams").glob("*.json")) if args == ["--all"] else args
failed = 0
for exam_id in ids:
    errors = validate(exam_id)
    print(f"{exam_id}: {'OK' if not errors else f'{len(errors)} problem(s)'}")
    for e in errors:
        print("   -", e)
    failed += bool(errors)
sys.exit(1 if failed else 0)
