"""Map problems to pages in text-based solution PDFs (those with a text layer).

For each solution document with a text layer, find where each problem's solution starts by
looking for "N." at the left margin, in order 1, 2, 3, ... . Problem N's pages run from its start
page to the page where N+1 starts (that page is dropped when N+1 starts at the very top).
Scanned/handwritten documents are reported so they can be mapped by eye.

Usage: python3 pipeline/map_solutions.py [exam_id ...]   (writes/updates data/solutions/<id>.json)
"""
import json, re, subprocess, sys

from common import DATA, load_json, sources

WORD = re.compile(r'<page width="([\d.]+)" height="([\d.]+)">|<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="[\d.]+" yMax="[\d.]+">([^<]*)</word>')


def starts(pdf, count):
    html = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    found, expected, page, width, height, skip = {}, 1, 0, 1, 1, False
    page_words = []
    for m in WORD.finditer(html):
        if m.group(1):
            page += 1
            width, height = float(m.group(1)), float(m.group(2))
            page_words.append([])
            continue
        page_words[-1].append((float(m.group(3)) / width, float(m.group(4)) / height, m.group(5)))
    # The numbering column is wherever the first "N." sits near the left edge; later numbers must
    # line up with it, which keeps "3." inside an equation from being mistaken for problem 3.
    col = None
    for p, words in enumerate(page_words, start=1):
        for x, y, w in words:
            m = re.fullmatch(r"(\d{1,2})\.", w)
            if not m:
                continue
            n = int(m.group(1))
            if col is None and x < 0.35 and n <= count:
                col, expected = x, n  # usually 1; a single-problem addendum may start later
            # accept the next number, or skip one or two whose label isn't in the text layer
            if col is not None and expected <= n <= min(count, expected + 2) and abs(x - col) < 0.015:
                found[n] = (p, y)
                expected = n + 1
    return found, len(page_words)


def page_ranges(found, count, npages):
    out = {}
    for n in range(1, count + 1):
        if n not in found:
            # label missing from the text layer: it lies between its neighbours
            prev = max((k for k in found if k < n), default=None)
            nxt = min((k for k in found if k > n), default=None)
            if prev and nxt:
                out[str(n)] = list(range(found[prev][0], found[nxt][0] + 1))
            continue
        p, _ = found[n]
        nxt = min((k for k in found if k > n), default=None)
        if nxt is not None:
            q, y = found[nxt]
            last = q - 1 if (q > p and y < 0.12) else q
        else:
            last = npages
        out[str(n)] = list(range(p, max(p, last) + 1))
    return out


def main(ids):
    for exam_id, src in sources().items():
        if (ids and exam_id not in ids) or not src["solutions"]:
            continue
        exam_path = DATA / "exams" / f"{exam_id}.json"
        count = len(load_json(exam_path)["problems"]) if exam_path.exists() else 20
        sol_path = DATA / "solutions" / f"{exam_id}.json"
        docs = {d["doc"]: d for d in (load_json(sol_path)["docs"] if sol_path.exists() else [])}
        for i, s in enumerate(src["solutions"]):
            pdf = DATA / "raw" / exam_id / f"sol{i}.pdf"
            text = (DATA / "text" / exam_id / f"sol{i}.txt").read_text(errors="ignore")
            if len(re.sub(r"\s", "", text)) < 500:
                status = "mapped by eye" if i in docs else "NEEDS MANUAL MAPPING (scanned)"
                print(f"{exam_id} sol{i}: {status} — {s['source']}")
                continue
            producer = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
            if "TeX" not in producer and s["source"].startswith("AMATYC"):
                # typed/scanned official solution sets: only trust a clean, complete 1..N sequence
                strict = True
            else:
                strict = False
            found, npages = starts(pdf, count)
            if strict and sorted(found) != list(range(1, count + 1)):
                print(f"{exam_id} sol{i}: NEEDS MANUAL MAPPING (non-TeX document, {len(found)}/{count} located) — {s['source']}")
                continue
            missing = [n for n in range(1, count + 1) if n not in found]
            interior = [n for n in missing if min(found, default=0) < n < max(found, default=0)]
            if interior:
                print(f"   note: #{interior} not labelled in text layer; placed between neighbours")
            missing = [n for n in missing if n not in interior]
            if len(found) > 1 and missing:  # partial text layer (e.g. typed headings on a scan): map by eye
                print(f"{exam_id} sol{i}: NEEDS MANUAL MAPPING (only {len(found)}/{count} located) — {s['source']}")
                continue
            docs[i] = {"doc": i, "pages": page_ranges(found, count, npages)}
            print(f"{exam_id} sol{i}: {len(found)}/{count} located over {npages} pages"
                  + (f" (covers only #{', #'.join(map(str, found))})" if missing else "") + f" — {s['source']}")
        sol_path.parent.mkdir(exist_ok=True)
        sol_path.write_text(json.dumps({"docs": [docs[k] for k in sorted(docs)]}, indent=1))


if __name__ == "__main__":
    main(set(sys.argv[1:]))
