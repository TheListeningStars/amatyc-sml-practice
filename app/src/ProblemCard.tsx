import { useState } from "react";
import type { Exam, Problem } from "./bank";
import { isCorrect } from "./bank";
import { MathText } from "./MathText";

const LETTERS = "ABCDE";

// "Solutions by Leo Livshutz (Truman College)" -> "Leo Livshutz"; "AMATYC official solutions" -> "AMATYC official"
const solutionLabel = (source: string) =>
  source.replace(/^Solutions by /, "").replace(/ \(.*\)$/, "").replace(/ solutions$/, "");

interface Props {
  index: number;
  problem: Problem;
  exam: Exam;
  topics: Record<string, string>;
  mode: "study" | "test" | "review";
  response?: string;
  onRespond?: (value: string) => void;
}

export function ProblemCard({ index, problem: p, exam, topics, mode, response, onRespond }: Props) {
  const [showAnswer, setShowAnswer] = useState(false);
  const [openSolution, setOpenSolution] = useState<number | null>(null);
  const answered = mode === "review";
  const correct = answered && isCorrect(p, response);

  return (
    <article className={`problem ${answered ? (correct ? "is-correct" : response ? "is-wrong" : "is-blank") : ""}`}>
      <header className="problem-head">
        <span className="problem-num">{index + 1}.</span>
        <a className="problem-source" href={exam.exam_url} target="_blank" rel="noreferrer">
          {exam.label} · #{p.n}
        </a>
        {p.flag && (
          <span className="chip warn-chip" title={p.key_note}>
            {p.flag === "voided" ? "voided / no key answer" : "answer not among choices"}
          </span>
        )}
        <span className="problem-topics">
          {p.topics.map((t) => (
            <span key={t} className="chip">
              {topics[t] ?? t}
            </span>
          ))}
        </span>
      </header>

      <MathText src={p.statement} as="div" />
      {p.figure && <img className="figure" src={p.figure} alt={`Figure for ${exam.label} problem ${p.n}`} />}

      {p.choices ? (
        <ol className="choices">
          {p.choices.map((c, i) => {
            const letter = LETTERS[i];
            const chosen = response === letter;
            const key = answered && p.answer.includes(letter);
            return (
              <li key={letter} className={`${chosen ? "chosen" : ""} ${key ? "key" : ""}`}>
                {mode === "test" ? (
                  <button type="button" onClick={() => onRespond?.(chosen ? "" : letter)}>
                    <b>{letter}.</b> <MathText src={c} />
                  </button>
                ) : (
                  <span>
                    <b>{letter}.</b> <MathText src={c} />
                  </span>
                )}
              </li>
            );
          })}
        </ol>
      ) : mode === "test" ? (
        <input
          className="free-response"
          placeholder="Your answer"
          value={response ?? ""}
          onChange={(e) => onRespond?.(e.target.value)}
        />
      ) : answered ? (
        <p className="free-response-review">Your answer: {response || "—"}</p>
      ) : null}

      {mode !== "test" && (
        <footer className="problem-actions no-print">
          {mode === "study" && (
            <button type="button" className="link" onClick={() => setShowAnswer((s) => !s)}>
              {showAnswer ? "Hide answer" : "Show answer"}
            </button>
          )}
          {(showAnswer || answered) && (
            <span className="answer">
              {p.flag === "voided" ? (
                <>Official key: no single answer</>
              ) : (
                <>
                  Official answer: <b>{p.answer.join(" or ")}</b>
                </>
              )}
              <a href={exam.key_url} target="_blank" rel="noreferrer">
                key
              </a>
            </span>
          )}
          {p.solutions?.map((s, i) => (
            <button key={s.url} type="button" className="link" onClick={() => setOpenSolution(openSolution === i ? null : i)}>
              {openSolution === i ? "Hide solution" : `Solution: ${solutionLabel(s.source)}`}
            </button>
          ))}
          {!p.solutions && <span className="muted">No published solution</span>}
        </footer>
      )}

      {(showAnswer || answered) && p.key_note && <p className="muted key-note">Key note: {p.key_note}</p>}

      {openSolution !== null && p.solutions && (
        <div className="solution">
          <p className="muted">
            {p.solutions[openSolution].source} — look for #{p.n}
            {p.solutions[openSolution].pages.length > 1 ? " on these pages" : " on this page"} (
            <a href={p.solutions[openSolution].url} target="_blank" rel="noreferrer">
              full document
            </a>
            ).
          </p>
          {p.solutions[openSolution].pages.map((src) => (
            <img key={src} src={src} alt={`Solution page for ${exam.label}`} loading="lazy" />
          ))}
        </div>
      )}
    </article>
  );
}
