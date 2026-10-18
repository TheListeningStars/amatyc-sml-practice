"""Validate transcribed exams, merge official answers and solutions, and write the problem bank.

Inputs:  pipeline/sources.json, pipeline/topics.json,
         data/exams/<id>.json   transcribed problems
         data/keys/<id>.json    official answers (+ notes, voided problems)
         data/solutions/<id>.json  optional: which pages of each solution document cover each problem
Outputs: app/public/bank.json, app/public/figures/<id>-<n>.png, app/public/solutions/<id>-sol<i>-<page>.jpg
Usage:   python3 pipeline/build.py   (requires Pillow; fails loudly on any validation problem)
"""
import json, sys

from PIL import Image

from common import DATA, LETTERS, ROOT, crop_figure, load_json, sources, topics, validate

OUT = ROOT / "app" / "public"


def solution_page(exam_id, doc, k):
    """Copy one rendered solution page into the app, downscaled to keep the site light."""
    dest = OUT / "solutions" / f"{exam_id}-sol{doc}-{k}.jpg"
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        page = Image.open(DATA / "pages" / exam_id / f"sol{doc}-{k}.png").convert("L")
        page.thumbnail((1100, 1500))
        page.save(dest, quality=72, optimize=True)
    return f"solutions/{dest.name}"


def main():
    srcs = sources()
    all_errors, problems, exams = [], [], []
    for exam_id, src in srcs.items():
        if not (DATA / "exams" / f"{exam_id}.json").exists():
            continue
        errors = validate(exam_id)
        if errors:
            all_errors += [f"{exam_id}: {e}" for e in errors]
            continue
        exam = load_json(DATA / "exams" / f"{exam_id}.json")
        key = load_json(DATA / "keys" / f"{exam_id}.json")
        sol_path = DATA / "solutions" / f"{exam_id}.json"
        sol_map = load_json(sol_path)["docs"] if sol_path.exists() else []
        voided = set(map(str, key.get("voided", [])))
        for p in exam["problems"]:
            n = str(p["n"])
            item = {
                "id": f"{exam_id}-{n}", "exam": exam_id, "n": p["n"],
                "statement": p["statement"], "choices": p["choices"],
                "answer": key["answers"].get(n, []), "topics": p["topics"],
            }
            if n in key.get("notes", {}):
                item["key_note"] = key["notes"][n]
            if n in voided:
                item["flag"] = "voided"
            elif p["choices"] and not all(a in LETTERS[: len(p["choices"])] for a in item["answer"]):
                item["flag"] = "no-matching-choice"
            if "figure" in p:
                dest = OUT / "figures" / f"{exam_id}-{n}.png"
                dest.parent.mkdir(parents=True, exist_ok=True)
                crop_figure(exam_id, p["figure"]).save(dest)
                item["figure"] = f"figures/{dest.name}"
            sols = []
            for d in sol_map:
                pages = d["pages"].get(n)
                if pages:
                    meta = src["solutions"][d["doc"]]
                    sols.append({"source": meta["source"], "url": meta["url"],
                                 "pages": [solution_page(exam_id, d["doc"], k) for k in pages]})
            if sols:
                item["solutions"] = sols
            problems.append(item)
        exams.append({"id": exam_id, "label": src["label"], "round": src["round"], "source": src["source"],
                      "exam_url": src["exam_link"], "key_url": src["files"]["key"],
                      "key_source": key.get("source", "")})
    if all_errors:
        print("\n".join(all_errors))
        sys.exit(1)
    exams.sort(key=lambda e: e["id"])
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "bank.json").write_text(json.dumps(
        {"topics": topics(), "exams": exams, "problems": problems}, ensure_ascii=False))
    print(f"{len(exams)} exams, {len(problems)} problems, "
          f"{sum('solutions' in p for p in problems)} with solutions -> {OUT / 'bank.json'}")


if __name__ == "__main__":
    main()
