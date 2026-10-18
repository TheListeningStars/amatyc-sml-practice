import { StrictMode, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "katex/dist/katex.min.css";
import "./styles.css";
import type { Bank } from "./bank";
import { examYear, loadBank } from "./bank";
import { PracticeTestPage } from "./PracticeTestPage";
import { ProblemSetPage } from "./ProblemSetPage";

type Tab = "sets" | "test";
const tabFromHash = (): Tab => (location.hash === "#test" ? "test" : "sets");

function App() {
  const [bank, setBank] = useState<Bank | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>(tabFromHash);

  useEffect(() => {
    loadBank().then(setBank, (e) => setError(String(e)));
    const onHash = () => setTab(tabFromHash());
    addEventListener("hashchange", onHash);
    return () => removeEventListener("hashchange", onHash);
  }, []);

  const exams = useMemo(() => new Map(bank?.exams.map((e) => [e.id, e])), [bank]);
  const years = useMemo<[number, number]>(() => {
    const ys = bank?.exams.map((e) => examYear(e.id)) ?? [0];
    return [Math.min(...ys), Math.max(...ys)];
  }, [bank]);

  return (
    <>
      <header className="site-head no-print">
        <h1>AMATYC Practice</h1>
        <nav>
          <a href="#sets" className={tab === "sets" ? "active" : ""}>
            Problem sets
          </a>
          <a href="#test" className={tab === "test" ? "active" : ""}>
            Practice test
          </a>
        </nav>
      </header>
      <main>
        {error && <p className="error">{error}</p>}
        {!bank && !error && <p className="muted">Loading problems…</p>}
        {bank && tab === "sets" && <ProblemSetPage bank={bank} exams={exams} years={years} />}
        {bank && tab === "test" && <PracticeTestPage bank={bank} exams={exams} years={years} />}
      </main>
      {bank && (
        <footer className="site-foot no-print">
          {bank.problems.length} problems from {bank.exams.length} AMATYC Student Mathematics League contests. Problems, answer keys
          and solutions are from the official{" "}
          <a href="https://www.amatyc.org/student-leagues/student-mathematics-league/competition-questions/" target="_blank" rel="noreferrer">
            AMATYC archive
          </a>
          ; topic tags are unofficial.
        </footer>
      )}
    </>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
