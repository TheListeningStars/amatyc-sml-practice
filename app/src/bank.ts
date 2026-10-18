// Problem bank types, loading, and the selection logic behind both generators.

export interface Exam {
  id: string;
  label: string;
  round: number;
  source: string;
  exam_url: string;
  key_url: string;
  key_source: string;
}

export interface Solution {
  source: string;
  url: string; // the full solution document
  pages: string[]; // rendered pages covering this problem
}

export interface Problem {
  id: string;
  exam: string;
  n: number;
  statement: string;
  choices: string[] | null; // null = free response
  answer: string[]; // accepted answers from the official key
  key_note?: string; // what the key says beyond the answer (corrector notes, "correct for all", ...)
  // voided: credited to everyone / not graded / no answer available
  // no-matching-choice: the key's answer is a value that is not one of the printed choices
  flag?: "voided" | "no-matching-choice";
  topics: string[];
  figure?: string;
  solutions?: Solution[];
}

export interface Bank {
  topics: Record<string, string>;
  exams: Exam[];
  problems: Problem[];
}

export async function loadBank(): Promise<Bank> {
  const res = await fetch("bank.json");
  if (!res.ok) throw new Error(`Could not load problem bank (${res.status})`);
  return res.json();
}

export const examYear = (examId: string) => Number(examId.slice(0, 4));

export interface Filters {
  topics: string[]; // empty = all topics
  yearFrom: number;
  yearTo: number;
  rounds: number[]; // empty = all rounds
  solutionsOnly: boolean;
}

export function matches(p: Problem, f: Filters, exams: Map<string, Exam>): boolean {
  const year = examYear(p.exam);
  if (year < f.yearFrom || year > f.yearTo) return false;
  if (f.rounds.length && !f.rounds.includes(exams.get(p.exam)!.round)) return false;
  if (f.solutionsOnly && !p.solutions) return false;
  return !f.topics.length || p.topics.some((t) => f.topics.includes(t));
}

// Small seeded PRNG so a set can be regenerated from its seed.
function mulberry32(seed: number) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export const newSeed = () => Math.floor(Math.random() * 2 ** 31);

function shuffle<T>(items: T[], rand: () => number): T[] {
  const a = [...items];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// Keep the original contest position as the only ordering signal: we never rate difficulty
// ourselves, but contest writers place problems roughly in the order they intend.
const byContestPosition = (a: Problem, b: Problem) => a.n - b.n;

export function problemSet(pool: Problem[], count: number, seed: number): Problem[] {
  return shuffle(pool, mulberry32(seed)).slice(0, count).sort(byContestPosition);
}

/**
 * A practice test draws `focusShare` of its problems from the focus topics and the rest from
 * everything else in the pool, falling back to whichever side has problems left.
 */
export function practiceTest(
  allPool: Problem[],
  focus: string[],
  count: number,
  focusShare: number,
  seed: number,
): Problem[] {
  const rand = mulberry32(seed);
  // a test needs a gradable answer, so leave out voided problems and keys with no matching choice
  const pool = allPool.filter((p) => !p.flag && p.answer.length > 0);
  const inFocus = (p: Problem) => focus.length > 0 && p.topics.some((t) => focus.includes(t));
  const focused = shuffle(pool.filter(inFocus), rand);
  const other = shuffle(pool.filter((p) => !inFocus(p)), rand);
  const wantFocused = Math.min(focused.length, focus.length ? Math.round(count * focusShare) : 0);
  const picked = focused.slice(0, wantFocused);
  picked.push(...other.slice(0, count - picked.length));
  // if the non-focus side ran short, top up with more focus problems
  picked.push(...focused.slice(wantFocused, wantFocused + count - picked.length));
  return picked.sort(byContestPosition);
}

const normalize = (s: string) => s.replace(/\s+/g, "").toUpperCase();

export function isCorrect(p: Problem, response: string | undefined): boolean {
  return !!response && p.answer.some((a) => normalize(a) === normalize(response));
}

// AMATYC SML scoring as printed on the official answer sheet: 2 per correct, -1/2 per wrong.
export function score(problems: Problem[], responses: Record<string, string>) {
  let correct = 0;
  let wrong = 0;
  for (const p of problems) {
    const r = responses[p.id];
    if (!r) continue;
    if (isCorrect(p, r)) correct++;
    else wrong++;
  }
  return { correct, wrong, blank: problems.length - correct - wrong, points: correct * 2 - wrong / 2 };
}
