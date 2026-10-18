import { useEffect, useMemo, useState } from "react";
import type { Bank, Exam, Filters, Problem } from "./bank";
import { isCorrect, matches, newSeed, practiceTest, score } from "./bank";
import { FilterPanel } from "./FilterPanel";
import { ProblemCard } from "./ProblemCard";

interface Props {
  bank: Bank;
  exams: Map<string, Exam>;
  years: [number, number];
}

interface TestRun {
  problems: Problem[];
  responses: Record<string, string>;
  startedAt: number;
  minutes: number; // 0 = untimed
  submitted: boolean;
  focus: string[];
}

interface HistoryEntry {
  date: string;
  focus: string[];
  correct: number;
  total: number;
  points: number;
}

const HISTORY_KEY = "amatyc-practice-history";

function readHistory(): HistoryEntry[] {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) ?? "[]");
  } catch {
    return [];
  }
}

function saveHistory(entries: HistoryEntry[]) {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(entries.slice(0, 50)));
  } catch {
    // storage unavailable (private mode etc.) — history is a convenience only
  }
}

const fmtTime = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;

export function PracticeTestPage({ bank, exams, years }: Props) {
  const [filters, setFilters] = useState<Filters>({
    topics: [],
    yearFrom: years[0],
    yearTo: years[1],
    rounds: [],
    solutionsOnly: false,
  });
  const [count, setCount] = useState(20);
  const [focusShare, setFocusShare] = useState(0.7);
  const [minutes, setMinutes] = useState(60);
  const [run, setRun] = useState<TestRun | null>(null);
  const [now, setNow] = useState(Date.now());
  const [history, setHistory] = useState(readHistory);

  // Focus topics steer the mix; everything else in the year/round range fills the rest.
  const pool = useMemo(
    () => bank.problems.filter((p) => matches(p, { ...filters, topics: [] }, exams)),
    [bank, filters, exams],
  );
  const topicCounts = useMemo(() => {
    const c: Record<string, number> = {};
    for (const p of pool) for (const t of p.topics) c[t] = (c[t] ?? 0) + 1;
    return c;
  }, [pool]);

  const remaining = run && run.minutes ? Math.max(0, Math.round(run.startedAt / 1000 + run.minutes * 60 - now / 1000)) : null;

  useEffect(() => {
    if (!run || run.submitted || !run.minutes) return;
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [run]);

  const submit = () => {
    if (!run || run.submitted) return;
    const s = score(run.problems, run.responses);
    const entry = { date: new Date().toISOString(), focus: run.focus, correct: s.correct, total: run.problems.length, points: s.points };
    const next = [entry, ...history];
    setHistory(next);
    saveHistory(next);
    setRun({ ...run, submitted: true });
    window.scrollTo({ top: 0 });
  };

  useEffect(() => {
    if (remaining === 0) submit();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [remaining]);

  const start = () => {
    const problems = practiceTest(pool, filters.topics, count, focusShare, newSeed());
    setNow(Date.now());
    setRun({ problems, responses: {}, startedAt: Date.now(), minutes, submitted: false, focus: filters.topics });
    window.scrollTo({ top: 0 });
  };

  if (!run) {
    return (
      <section>
        <div className="panel">
          <FilterPanel
            topics={bank.topics}
            topicCounts={topicCounts}
            years={years}
            filters={filters}
            onChange={setFilters}
            topicLabel="Focus topics (optional)"
          />
          <div className="actions">
            <label>
              Problems
              <input type="number" min={1} max={pool.length} value={count} onChange={(e) => setCount(Math.max(1, Number(e.target.value) || 1))} />
            </label>
            <label>
              Time limit (min, 0 = none)
              <input type="number" min={0} value={minutes} onChange={(e) => setMinutes(Math.max(0, Number(e.target.value) || 0))} />
            </label>
            {filters.topics.length > 0 && (
              <label>
                Focus share {Math.round(focusShare * 100)}%
                <input type="range" min={0.3} max={1} step={0.1} value={focusShare} onChange={(e) => setFocusShare(Number(e.target.value))} />
              </label>
            )}
            <button type="button" className="primary" disabled={!pool.length} onClick={start}>
              Start test
            </button>
          </div>
          <p className="muted">
            Scored like the AMATYC SML: +2 per correct answer, −½ per wrong answer, 0 for blanks. The real contest is 20 problems in 60 minutes.
          </p>
        </div>
        {history.length > 0 && (
          <div className="panel">
            <h3>Recent tests</h3>
            <table className="history">
              <tbody>
                {history.slice(0, 10).map((h) => (
                  <tr key={h.date}>
                    <td>{new Date(h.date).toLocaleDateString()}</td>
                    <td>
                      {h.correct}/{h.total} correct
                    </td>
                    <td>{h.points} pts</td>
                    <td className="muted">{h.focus.map((t) => bank.topics[t] ?? t).join(", ") || "mixed"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    );
  }

  const s = score(run.problems, run.responses);
  const byTopic: Record<string, [number, number]> = {};
  for (const p of run.problems)
    for (const t of p.topics) {
      const e = (byTopic[t] ??= [0, 0]);
      e[1]++;
      if (isCorrect(p, run.responses[p.id])) e[0]++;
    }
  const answeredCount = Object.values(run.responses).filter(Boolean).length;

  return (
    <section>
      <div className="panel test-bar">
        {run.submitted ? (
          <>
            <strong>
              Score: {s.points} / {run.problems.length * 2}
            </strong>
            <span>
              {s.correct} correct · {s.wrong} wrong · {s.blank} blank
            </span>
            <button type="button" onClick={() => setRun(null)}>
              New test
            </button>
          </>
        ) : (
          <>
            <span>
              {answeredCount}/{run.problems.length} answered
            </span>
            {remaining !== null && <strong className={remaining < 300 ? "warn" : ""}>{fmtTime(remaining)}</strong>}
            <button type="button" className="primary" onClick={submit}>
              Submit
            </button>
          </>
        )}
      </div>

      {run.submitted && (
        <div className="panel">
          <h3>By topic</h3>
          <div className="topic-results">
            {Object.entries(byTopic)
              .sort((a, b) => b[1][1] - a[1][1])
              .map(([t, [c, n]]) => (
                <span key={t} className="chip">
                  {bank.topics[t] ?? t}: {c}/{n}
                </span>
              ))}
          </div>
        </div>
      )}

      <div className="problem-list">
        {run.problems.map((p, i) => (
          <ProblemCard
            key={p.id}
            index={i}
            problem={p}
            exam={exams.get(p.exam)!}
            topics={bank.topics}
            mode={run.submitted ? "review" : "test"}
            response={run.responses[p.id]}
            onRespond={(v) => setRun({ ...run, responses: { ...run.responses, [p.id]: v } })}
          />
        ))}
      </div>
    </section>
  );
}
