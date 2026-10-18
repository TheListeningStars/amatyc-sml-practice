# Transcribing an exam

You are turning one AMATYC Student Mathematics League exam into two JSON files:

- `data/exams/<id>.json`: the problems, exactly as printed, in Markdown + LaTeX
- `data/keys/<id>.json`: the official answers, exactly as the answer key gives them

Project root: `/Users/arshshah/Desktop/Coding/Personal Projects/AMATYC_Generator` (all paths below are relative to it).

## Hard rules

1. **Faithful transcription.** Copy every problem word-for-word and every number, symbol and choice exactly.
   Do not "fix" math, reword or simplify, even if the problem seems wrong. You may fix an obvious
   *English spelling* typo (e.g. "fuction" → "function"), nothing else.
2. **Never solve problems.** Never write solutions. Never rate difficulty. Never guess an answer: answers come
   only from the key document. If the key is unreadable for a problem, say so in your report (see below).
3. Only write the files for the exam(s) you were assigned. Do not edit anything else.

## Inputs (for exam `<id>`)

- `data/pages/<id>/exam-<page>.png`: rendered exam pages. **This is the source of truth.** View them with the Read tool.
  Zoom in when needed: `python3 -c "from PIL import Image; im=Image.open('data/pages/<id>/exam-1.png'); w,h=im.size; im.crop((0,0,w,h//2)).save('/tmp/zoom.png')"` then Read the crop.
  (Use your scratchpad directory instead of /tmp if you have one.)
- `data/text/<id>/exam.txt`: the PDF's text layer, if any. Good for wording but **drops superscripts, fractions,
  radicals and minus signs**, so never trust its math. (Empty for scanned exams.)
- `data/raw/<id>/source.tex`: the original LaTeX for some 1985–1999 exams. Use it as a precise reference for
  math, then convert it to this project's conventions (no Scientific WorkPlace macros, no `%TCIMACRO` lines).
- Key: `data/pages/<id>/key-<page>.png` (rendered key) and/or `data/text/<id>/key.txt` (text of a .pdf/.doc/.tex key).
  - Some key documents cover **several exams** (e.g. "Short Solutions" files with November, February and
    March/April sections). Use only the section whose date heading matches your exam. In those files the answer
    letter is the letter in the left margin next to each problem number.
  - For 1996–1999 exams the answers are printed on the **last page of the exam PDF** ("Answers - November 1996").
  - `data/pages/<id>/alt<i>-*.png` / `data/text/<id>/alt<i>.txt` are second copies of the key from another site.
    You may glance at them, but **record what the official key (`key-*`) says**. (Keys are cross-checked
    against these automatically afterwards, so a full comparison is not required.)
- `data/pages/<id>/sol<i>-*.png`: solution documents. Ignore them, except: when the key document *is* a short-solutions
  file, its margin letters are the key.

## Output 1: `data/exams/<id>.json`

Use `data/exams/2019-fall.json` and `data/exams/2024-spring.json` as style references. Shape:

```json
{
  "id": "<id>",
  "problems": [
    {"n": 1, "topics": ["number-theory"],
     "statement": "Let $M$ be the smallest positive integer ... Find $M+N$.",
     "choices": ["$70$", "$72$", "$74$", "$76$", "$78$"]},
    {"n": 2, "topics": ["geometry"],
     "statement": "Refer to the figure. Find ...",
     "choices": ["$15^\\circ$", "$20^\\circ$", "$22^\\circ$", "$26^\\circ$", "$30^\\circ$"],
     "figure": {"page": 2, "box": [0.845, 0.098, 0.985, 0.36]}}
  ]
}
```

- `n`: problem number, 1..N in order. Include **every** problem printed on the exam (older exams may not have 20).
- `statement`: the problem text without its number and without the choices.
  - Math in `$...$` (inline) or `$$...$$` (displayed equations/systems). All variables, numbers-with-operators, and
    expressions go in math mode: `$x^2 + 3$`, `$f(x)$`, `$\triangle ABC$`, `$\overline{AB}$`, `$\angle A$`, `$30^\circ$`.
    Plain numbers in prose may stay as text ("a circle of radius 6").
  - Fractions `\frac{a}{b}` (use `\dfrac` for a prominent stand-alone fraction), roots `\sqrt[3]{x}`,
    systems `\begin{cases} ... \\ ... \end{cases}`, piecewise the same way, matrices `\begin{bmatrix}..\end{bmatrix}`,
    `\log_2`, `\sin`, `\pi`, `\le`, `\ge`, `\ne`, `\cdot`, `\times`, `\ldots`, `\mathbb{R}`, `\binom{n}{k}`, `\text{...}` for words inside math.
  - A literal dollar sign is `\$` (e.g. `\$8.30`). `**bold**` and `*italic*` work for emphasised words
    (e.g. **not**, *exactly*). Underlined words become `**...**`.
  - Line/paragraph breaks: `\n\n` between parts such as "(i) ... \n\n(ii) ..." or numbered statements "I. ... II. ...".
  - Tables of values: use a `$$\begin{array}{c|c|c} ... \end{array}$$`.
- `choices`: list of the answer choices in order (A first), each a string, math in `$...$`.
  `null` if the problem has no printed choices (free response). Keep "E. none of these" etc. as `"none of these"`.
  If the choices themselves are pictures (graphs), write `"(graph A)"`, `"(graph B)"`, … and make the figure crop cover them.
- `topics`: 1–3 ids from `pipeline/topics.json`, most relevant first (see guidance below).
- `figure` (only if the problem has a picture/diagram/table-image that the text can't replace):
  `page` = exam page number, `box` = `[x0, y0, x1, y1]` as **fractions of the page width/height** (0–1).
  Get pixel sizes with PIL (`Image.open(path).size`) and divide. Leave a small margin around the drawing.
  If unrelated text intrudes into the box, add `"erase": [[x0,y0,x1,y1], ...]` (same units) to white it out.
  **Then look at your crop**: `python3 pipeline/check.py --crop <id> <n>` writes it to `data/review/crops/`; Read it
  and adjust until it shows the whole figure and nothing else. Every figure must be checked this way.
- Labels that appear only inside a diagram stay in the figure; don't repeat them in the text.
- Use the exam's own wording for references like "the accompanying diagram" / "shown at the left".
- `note` (optional): a short note for the reviewer if something in the source is genuinely illegible or ambiguous.

JSON escaping: every LaTeX backslash is doubled in the file (`"$\\frac{1}{2}$"`). Use `“`/`”` or plain
quotes for quotation marks inside strings (escape `"` as `\"`).

## Output 2: `data/keys/<id>.json`

```json
{
  "source": "AMATYC official answer key",
  "answers": {"1": ["E"], "2": ["B"], "13": ["C", "D"], "9": ["3:21:49"], "11": ["322"], "15": []},
  "notes": {"13": "Key accepts C or D", "11": "Key: 322; corrector note \"Correct or blank\"", "15": "Correct for all students"},
  "voided": ["15"]
}
```

- `source`: what the key document is, e.g. `"AMATYC official answer key"`, `"Answers printed in the exam (Marta Hidegkuti archive)"`,
  `"SML official short solutions"`, `"Official key (Marta Hidegkuti archive)"`.
- `answers`: one entry per problem, `"n": [accepted answers]`, exactly as the key gives them. Normally one letter.
  Two letters if the key accepts either. A number/expression if the key gives one (free-response problems, or a
  key that prints a value instead of a letter).
- `notes`: anything else the key says about a problem (text in the "Local Corrector" column, "C or B", "Correct or blank,
  never wrong", "not graded", "misprint", "X") quoted or closely paraphrased. **Required** whenever an answer
  is not one of the problem's choice letters.
- Omit `notes` / `voided` when empty.
- `voided`: problem numbers the key says count for everyone or were not graded (`"Correct for all students"`,
  `"X ... not graded"`). Their `answers` entry may be `[]` or hold the value the key prints. Each needs a note.

## Topics (`pipeline/topics.json`)

`algebra` (equations, inequalities, systems, binary operations, manipulation), `polynomials` (roots, factoring,
remainder theorem, rational functions' numerators/denominators), `functions` (graphs, composition, inverses,
asymptotes, transformations, domain/range), `logarithms-exponents`, `sequences-series`, `complex-numbers`,
`vectors-matrices` (vectors, matrices, determinants, linear systems in 3D), `number-theory` (divisibility, primes,
digits, bases, modular arithmetic, Diophantine equations), `combinatorics` (counting, arrangements, paths),
`probability` (probability, expected value, statistics/averages), `geometry` (synthetic plane & solid geometry,
areas, volumes), `coordinate-geometry` (lines, conics, distance in the plane, polar curves), `trigonometry`,
`logic` (knights/knaves, puzzles, true/false statements, cryptarithms), `word-problems` (rates, mixtures, money,
units, clocks, work, everyday contexts). Tag what a student would need to know, not surface keywords.

## Check your work (required)

1. `python3 pipeline/check.py <id>` must print `OK` (schema, numbering, key/answer consistency, KaTeX).
2. Re-read every page image once more against your JSON, problem by problem: numbers, signs, exponents,
   subscripts, choice order, every choice present.
3. Every figure crop viewed with `--crop`.

## Report back

For each exam: problem count, number of figures, any key oddities (voided, numeric answers, notes), any place where
the official key and an `alt` key disagree, anything illegible, and the final `check.py` output.
