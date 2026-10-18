# Mapping scanned solution pages to problems

Project root: `/Users/arshshah/Desktop/Coding/Personal Projects/AMATYC_Generator`.

For exam `<id>`, solution document `i` (listed in `pipeline/sources.json` under that exam's `solutions`, in order) is
rendered as `data/pages/<id>/sol<i>-<page>.png` (pages numbered from 1). Your job is to record, for every problem,
which page(s) of that document contain its solution.

1. Look at every page image of the document (Read tool). Solutions are usually headed by the problem number
   ("1.", "#7", "13. Method A", a circled number, or an answer letter in the margin next to the number).
2. A problem's pages = the page where its solution starts, plus any following pages it continues onto.
3. Some documents cover **several exams** (e.g. "Short Solutions" files with November / January-February /
   March-April sections). Map only the section whose date heading matches your exam, using the page numbers of the
   whole document.
4. If a problem has no solution in the document, leave it out.
5. Write `data/solutions/<id>.json`. **Keep any existing entries for other documents** — read the file first, then add
   or replace only the entry for your document:
   ```json
   {"docs": [{"doc": 0, "pages": {"1": [1], "2": [1, 2], "3": [2]}}]}
   ```
   (`docs` sorted by `doc`.) Use `json` in Python to read-modify-write so the file stays valid.
6. Do not solve problems, do not transcribe solutions, do not edit any other files.

Report: for each document, the page range of each problem in one line (e.g. `1:1 2:1-2 3:2 ...`) and anything unclear.
