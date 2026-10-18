# Verifying a transcribed exam

Project root: `/Users/arshshah/Desktop/Coding/Personal Projects/AMATYC_Generator`. Read `pipeline/TRANSCRIBE.md` first:
its conventions and hard rules apply here too (faithful transcription, never solve, never invent answers).

Someone else transcribed exam `<id>` into `data/exams/<id>.json` and `data/keys/<id>.json`. Your job is an
independent, problem-by-problem check against the source images, fixing whatever is wrong.

## Working files — important

Several agents run at the same time. Put **all** scratch files (zoom crops, helper scripts) in
`data/review/work/<id>/` (create it). Never write to the shared scratchpad or any other exam's folder, and never run a
script you did not write yourself in this session.

## What to check, for every problem

Compare the JSON against `data/pages/<id>/exam-*.png` (zoom into regions; read every page in full):
1. Statement wording: nothing missing, added or reworded (apart from obvious English spelling fixes).
2. Every number, sign, exponent, subscript, fraction, radical, inequality direction, variable name.
3. Choices: all present, correct order, correct content, correct count; `null` only if no choices are printed.
4. Figures: every problem that has a picture has a `figure`; view each crop with
   `python3 pipeline/check.py --crop <id> <n>` and fix the box if it cuts anything off or includes unrelated text.
5. Topics: sensible (1–3 ids from `pipeline/topics.json`).

Then the key: compare `data/keys/<id>.json` with the key images (`data/pages/<id>/key-*.png`; for 1996–1999 the
answers page at the end of the exam; for short-solutions files the correct section's margin letters). Every answer,
every note, every voided entry.

## Fixing

Edit the JSON directly (Edit tool, or a small Python read-modify-write you write yourself). Keep the schema. Then run
`python3 pipeline/check.py <id>` until it prints OK.

## Log

Write `data/review/<id>.md`: one line per change (`#7 choice C: $-3$ -> $3$ (sign missing)`), or "No changes" — plus
anything you could not resolve. Report the same summary back.
