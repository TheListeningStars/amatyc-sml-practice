# Ingestion status (2026-10-17)

Complete: 65 exams / 1,296 problems.

- Transcribed (TRANSCRIBE.md), then independently verified problem-by-problem against the page images
  (VERIFY.md; per-exam logs in this folder). Verification fixes included a swapped key pair in 2001-fall
  (#16/#17, from a scratch-script collision during transcription), figure-crop tightening, and conflict notes.
- Keys cross-checked against every independent source (crosscheck_keys.py); every disagreement was re-read on
  the official key image and is recorded in key_disagreements.json.
- 2002-fall #20 recovered from a misfiled short-solutions page; 1985-spring #5/#15/#18 from the LaTeX
  correct-answer markers (noted in the key).
- Still voided (no usable official answer): 1985-spring #13 #20, 1995-fall #16 #19, 2000-fall #18, and the
  "correct for all students" problems (2005-spring #6, 2008-fall #15, 2009-spring #15, 2012-spring #14,
  2013-spring #14, 2016-spring #19, 2017-spring #1).
- Flagged "answer not among choices": 2016-fall #16 (key prints the value 541 with "correct or blank, never wrong").

Known cosmetic issues: a faint sliver of text at the top of the 2009-fall #14 figure; scan bleed-through in
some 1999–2003 figure crops.
