import { useMemo, useState } from "react";
import type { Bank, Exam, Filters } from "./bank";
import { matches, newSeed, problemSet } from "./bank";
import { FilterPanel } from "./FilterPanel";
import { ProblemCard } from "./ProblemCard";

interface Props {
  bank: Bank;
  exams: Map<string, Exam>;
  years: [number, number];
}

export function ProblemSetPage({ bank, exams, years }: Props) {
  const [filters, setFilters] = useState<Filters>({
    topics: [],
    yearFrom: years[0],
    yearTo: years[1],
    rounds: [],
    solutionsOnly: false,
  });
  const [count, setCount] = useState(10);
  const [seed, setSeed] = useState<number | null>(null);

  const pool = useMemo(() => bank.problems.filter((p) => matches(p, filters, exams)), [bank, filters, exams]);
  const topicCounts = useMemo(() => {
    const c: Record<string, number> = {};
    const unTopiced = { ...filters, topics: [] };
    for (const p of bank.problems) if (matches(p, unTopiced, exams)) for (const t of p.topics) c[t] = (c[t] ?? 0) + 1;
    return c;
  }, [bank, filters, exams]);
  const problems = useMemo(() => (seed === null ? [] : problemSet(pool, count, seed)), [pool, count, seed]);

  return (
    <section>
      <div className="panel no-print">
        <FilterPanel
          topics={bank.topics}
          topicCounts={topicCounts}
          years={years}
          filters={filters}
          onChange={setFilters}
          topicLabel="Topics (any of)"
        />
        <div className="actions">
          <label>
            Problems
            <input
              type="number"
              min={1}
              max={Math.max(1, pool.length)}
              value={count}
              onChange={(e) => setCount(Math.max(1, Number(e.target.value) || 1))}
            />
          </label>
          <span className="muted">{pool.length} problems match</span>
          <button type="button" className="primary" disabled={!pool.length} onClick={() => setSeed(newSeed())}>
            {seed === null ? "Generate set" : "New set"}
          </button>
          {problems.length > 0 && (
            <button type="button" onClick={() => window.print()}>
              Print
            </button>
          )}
        </div>
      </div>

      {problems.length > 0 && (
        <div className="problem-list">
          <h2 className="print-only">AMATYC practice set</h2>
          {problems.length < count && (
            <p className="muted no-print">Only {problems.length} problems match these filters.</p>
          )}
          {problems.map((p, i) => (
            <ProblemCard key={p.id} index={i} problem={p} exam={exams.get(p.exam)!} topics={bank.topics} mode="study" />
          ))}
          <div className="print-only answer-list">
            <h3>Answers</h3>
            {problems.map((p, i) => (
              <span key={p.id}>
                {i + 1}. {p.answer.join("/")}
              </span>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
