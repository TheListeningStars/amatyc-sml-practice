# AMATYC Practice

Problem set and practice test generator for the AMATYC Student Mathematics League (SML).
See `exec_summary.md` for the goals and ground rules: answers and solutions come only from
official/published sources; we never write solutions or rate difficulty.

## Coverage

65 contests, 1,296 problems: Spring 1985 and 1986, then every round from Fall 1995 to Spring 2025
(including the April "Round 3" contests of 1997–2002). No contests were published for Fall 2020 /
Spring 2021, and 1987–1994 are not available online.

- Sources: the official AMATYC archive (Fall 2003 onward) and teaching.martahidegkuti.com (everything
  older, plus second copies of 2003–2017 keys used for cross-checking).
- Answers: always from an official key, or from answers printed with the exam in the archive. Problems the
  key voided (or where no answer survives) are labelled and kept out of practice tests.
- Solutions (660 problems): AMATYC official solutions (2011–2020), SML short solutions (2000–2003),
  Leo Livshutz (2007–2014) and Marta Hidegkuti (2013, 2017), shown as the original pages.
- Topic tags are ours (the sources have none).

## Layout

```
pipeline/
  sources.json        every exam: exam/key PDFs, second-source keys, solution documents
  topics.json         topic taxonomy
  fetch.py            download -> data/raw, render pages (macOS Quartz) -> data/pages, text -> data/text
  TRANSCRIBE.md       how exams are transcribed into data/exams + data/keys
  VERIFY.md           how each transcription is independently re-checked against the page images
  check.py            validate exam + key JSON (schema, numbering, key consistency, KaTeX); --crop previews figures
  crosscheck_keys.py  compare every key with independent sources (sheet text, archive copy, Livshutz, LaTeX markers)
  map_solutions.py    map problems to pages in text-based solution PDFs (scanned ones: MAP_SOLUTIONS.md)
  build.py            validate + merge everything -> app/public/bank.json (+ figures, solution page images)
data/
  exams/<id>.json     transcribed problems (Markdown + $LaTeX$), topics, figure crop boxes
  keys/<id>.json      official answers, key notes, voided problems
  solutions/<id>.json which pages of each solution document cover each problem
  review/             verification logs per exam, reviewed key disagreements
app/                  static React + KaTeX site (Vite)
```

## Updating the bank

Requires macOS (Quartz rendering via pyobjc, `textutil`), Python 3 with Pillow, poppler (`pdftotext`),
and Node (for the KaTeX check, run after `npm install` in `app/`).

```sh
python3 pipeline/fetch.py              # optional: exam ids to limit; --rerender to redraw pages
python3 pipeline/check.py --all
python3 pipeline/crosscheck_keys.py    # must report no unreviewed disagreements
python3 pipeline/map_solutions.py
python3 pipeline/build.py
```

To add an exam: add it to `sources.json`, fetch it, transcribe per `TRANSCRIBE.md`, verify per `VERIFY.md`,
map its solutions, then build.

## Running the site

```sh
cd app
npm install
npm run dev        # development
npm run build      # static site in app/dist — serve it with any web server
```

### Live site (GitHub Pages)

Live at https://thelisteningstars.github.io/amatyc-sml-practice/ (the old `/amatyc-practice/` address redirects there).
Every push to `main` builds `app/` and publishes it to GitHub Pages
(`.github/workflows/pages.yml`). The problem bank in `app/public/` is committed, so after changing data run
`python3 pipeline/build.py` locally and commit the result.

The downloaded PDFs and page renders (`data/raw`, `data/pages`, `data/text`) are not in the repo; recreate them
with `python3 pipeline/fetch.py` before re-transcribing or rebuilding figures.

Or self-host with Docker:

```sh
cd app
docker build -t amatyc-sml-practice .
docker run -p 8080:80 amatyc-sml-practice
```
