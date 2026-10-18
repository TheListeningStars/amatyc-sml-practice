"""Download the files listed in sources.json and prepare them for transcription.

Usage: python3 pipeline/fetch.py [--rerender] [exam_id ...]

Per exam, into data/raw/<id>/ and data/pages/<id>/ (data/text/<id>/ for extracted text):
  exam    the problems              -> exam.pdf, exam-<n>.png
  key     official answer key       -> key.<ext>, key-<n>.png (PDF) or key.txt (.doc/.tex)
  alt<i>  second-source keys, used only to cross-check the official key
  sol<i>  solution documents        -> sol<i>.pdf, sol<i>-<n>.png
Scanned exams are rendered at a higher resolution. Pages are rendered with macOS Quartz
(render_quartz.py): poppler draws the Symbol-font glyphs in several Mac Word PDFs as empty boxes.
Requires macOS (Quartz via pyobjc, textutil) and poppler (pdftotext).
"""
import json, shutil, subprocess, sys, urllib.request
from pathlib import Path

from render_quartz import render

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def download(url, dest):
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    dest.write_bytes(urllib.request.urlopen(req, timeout=60).read())


def prepare(src, exam_id, kind, dpi, force=False):
    pages = DATA / "pages" / exam_id
    text = DATA / "text" / exam_id / f"{kind}.txt"
    pages.mkdir(parents=True, exist_ok=True)
    text.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix == ".pdf":
        if not any(pages.glob(f"{kind}-*.png")) or force:
            render(src, pages / kind, dpi)
        subprocess.run(["pdftotext", "-layout", src, text], check=True)
    elif src.suffix == ".doc":
        subprocess.run(["textutil", "-convert", "txt", "-output", text, src], check=True, capture_output=True)
    else:  # .tex and other plain text
        shutil.copy(src, text)


def main(ids, force=False):
    exams = json.loads((ROOT / "pipeline" / "sources.json").read_text())["exams"]
    for exam in exams:
        if ids and exam["id"] not in ids:
            continue
        jobs = [("exam", exam["files"]["exam"]), ("key", exam["files"]["key"])]
        jobs += [(f"alt{i}", u) for i, u in enumerate(exam.get("alt_keys", []))]
        jobs += [(f"sol{i}", s["url"]) for i, s in enumerate(exam["solutions"])]
        for kind, url in jobs:
            ext = Path(urllib.request.url2pathname(url.split("/")[-1])).suffix.lower()
            raw = DATA / "raw" / exam["id"] / f"{kind}{ext}"
            download(url, raw)
            prepare(raw, exam["id"], kind, 200 if exam.get("scanned") and kind in ("exam", "key") else 150, force)
        print("ok", exam["id"])


if __name__ == "__main__":
    args = sys.argv[1:]
    main(set(a for a in args if a != "--rerender"), force="--rerender" in args)
