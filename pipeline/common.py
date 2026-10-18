"""Shared helpers: loading exam/key files, validation, and figure cropping."""
import json, subprocess
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LETTERS = "ABCDEF"


def load_json(path):
    return json.loads(Path(path).read_text())


def sources():
    return {e["id"]: e for e in load_json(ROOT / "pipeline" / "sources.json")["exams"]}


def topics():
    return load_json(ROOT / "pipeline" / "topics.json")


def unescaped_dollars(s):
    return s.replace("\\$", "").count("$")


def crop_figure(exam_id, fig):
    """Return the figure image. Boxes are page fractions [x0, y0, x1, y1]; optional "erase"
    boxes (same units) are painted white to remove neighbouring text."""
    page = Image.open(DATA / "pages" / exam_id / f"exam-{fig['page']}.png").convert("RGB")
    w, h = page.size
    px = lambda b: (round(b[0] * w), round(b[1] * h), round(b[2] * w), round(b[3] * h))
    draw = ImageDraw.Draw(page)
    for box in fig.get("erase", []):
        draw.rectangle(px(box), fill="white")
    return page.crop(px(fig["box"]))


def _check_box(box, where, errors):
    if not (isinstance(box, list) and len(box) == 4 and all(isinstance(v, (int, float)) for v in box)):
        errors.append(f"{where}: box must be four numbers")
    elif not (0 <= box[0] < box[2] <= 1 and 0 <= box[1] < box[3] <= 1):
        errors.append(f"{where}: box {box} must satisfy 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1")


def validate(exam_id, katex=True):
    """Return a list of problems with data/exams/<id>.json and data/keys/<id>.json."""
    errors = []
    topic_ids = set(topics())
    exam_path = DATA / "exams" / f"{exam_id}.json"
    key_path = DATA / "keys" / f"{exam_id}.json"
    try:
        exam = load_json(exam_path)
    except Exception as e:
        return [f"{exam_path.name}: {e}"]
    try:
        key = load_json(key_path)
    except Exception as e:
        return [f"{key_path.name}: {e}"]

    if exam.get("id") != exam_id:
        errors.append(f"exam id {exam.get('id')!r} != {exam_id!r}")
    problems = exam.get("problems", [])
    nums = [p.get("n") for p in problems]
    if nums != list(range(1, len(problems) + 1)):
        errors.append(f"problem numbers must be 1..N in order, got {nums}")

    answers = key.get("answers", {})
    voided = set(map(str, key.get("voided", [])))
    notes = key.get("notes", {})
    if sorted(answers, key=int) != [str(n) for n in nums]:
        errors.append(f"key has answers for {sorted(answers, key=int)} but exam has problems {nums}")
    for n in voided:
        if n not in notes:
            errors.append(f"key #{n}: voided problems need a note explaining why")

    for p in problems:
        w = f"#{p.get('n')}"
        extra = set(p) - {"n", "statement", "choices", "topics", "figure", "note"}
        if extra:
            errors.append(f"{w}: unknown fields {sorted(extra)}")
        st = p.get("statement")
        if not isinstance(st, str) or not st.strip():
            errors.append(f"{w}: empty statement")
        elif unescaped_dollars(st) % 2:
            errors.append(f"{w}: unbalanced $ in statement")
        ts = p.get("topics", [])
        if not (1 <= len(ts) <= 3) or set(ts) - topic_ids:
            errors.append(f"{w}: topics must be 1-3 of {sorted(topic_ids)}, got {ts}")
        ch = p.get("choices")
        if ch is not None:
            if not (isinstance(ch, list) and 2 <= len(ch) <= 6 and all(isinstance(c, str) and c.strip() for c in ch)):
                errors.append(f"{w}: choices must be null or a list of 2-6 non-empty strings")
            elif any(unescaped_dollars(c) % 2 for c in ch):
                errors.append(f"{w}: unbalanced $ in a choice")
        fig = p.get("figure")
        if fig is not None:
            page = DATA / "pages" / exam_id / f"exam-{fig.get('page')}.png"
            if not page.exists():
                errors.append(f"{w}: figure page {fig.get('page')} does not exist")
            _check_box(fig.get("box"), f"{w} figure", errors)
            for b in fig.get("erase", []):
                _check_box(b, f"{w} figure erase", errors)

        n = str(p.get("n"))
        ans = answers.get(n)
        if n in voided:
            continue
        if not (isinstance(ans, list) and ans and all(isinstance(a, str) and a.strip() for a in ans)):
            errors.append(f"{w}: key answer must be a non-empty list of strings, got {ans!r}")
        elif isinstance(ch, list):
            letters = LETTERS[: len(ch)]
            if not all(len(a) == 1 and a in letters for a in ans) and n not in notes:
                errors.append(f"{w}: key answer {ans} is not among choices {letters} (add a key note if the key really says this)")

    if katex and not errors:
        errors += katex_errors(exam)
    return errors


def katex_errors(exam):
    texts = []
    for p in exam["problems"]:
        texts.append((f"#{p['n']} statement", p["statement"]))
        for i, c in enumerate(p.get("choices") or []):
            texts.append((f"#{p['n']} choice {LETTERS[i]}", c))
    res = subprocess.run(["node", ROOT / "pipeline" / "katex_check.mjs"], input=json.dumps(texts),
                         capture_output=True, text=True, cwd=ROOT / "app")
    if res.returncode:
        return [f"katex check failed to run: {res.stderr.strip()[:300]}"]
    return json.loads(res.stdout)
