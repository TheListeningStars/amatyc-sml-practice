import type { Filters } from "./bank";

interface Props {
  topics: Record<string, string>;
  topicCounts: Record<string, number>;
  years: [number, number];
  filters: Filters;
  onChange: (f: Filters) => void;
  topicLabel: string;
}

export function FilterPanel({ topics, topicCounts, years, filters, onChange, topicLabel }: Props) {
  const set = (patch: Partial<Filters>) => onChange({ ...filters, ...patch });
  const toggle = <T,>(list: T[], v: T) => (list.includes(v) ? list.filter((x) => x !== v) : [...list, v]);
  const yearOptions = Array.from({ length: years[1] - years[0] + 1 }, (_, i) => years[0] + i);

  return (
    <div className="filters">
      <fieldset>
        <legend>
          {topicLabel}
          {filters.topics.length > 0 && (
            <button type="button" className="link" onClick={() => set({ topics: [] })}>
              clear
            </button>
          )}
        </legend>
        <div className="topic-grid">
          {Object.entries(topics).map(([id, label]) => (
            <label key={id} className={`topic ${filters.topics.includes(id) ? "on" : ""}`}>
              <input
                type="checkbox"
                checked={filters.topics.includes(id)}
                onChange={() => set({ topics: toggle(filters.topics, id) })}
              />
              {label} <span className="count">{topicCounts[id] ?? 0}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <div className="filter-row">
        <label>
          Years
          <select value={filters.yearFrom} onChange={(e) => set({ yearFrom: Number(e.target.value) })}>
            {yearOptions.map((y) => (
              <option key={y}>{y}</option>
            ))}
          </select>
          to
          <select value={filters.yearTo} onChange={(e) => set({ yearTo: Number(e.target.value) })}>
            {yearOptions.map((y) => (
              <option key={y}>{y}</option>
            ))}
          </select>
        </label>
        <span className="rounds">
          Round
          {[1, 2, 3].map((r) => (
            <label key={r}>
              <input
                type="checkbox"
                checked={!filters.rounds.length || filters.rounds.includes(r)}
                onChange={() => {
                  const current = filters.rounds.length ? filters.rounds : [1, 2, 3];
                  const next = toggle(current, r);
                  set({ rounds: next.length === 3 ? [] : next });
                }}
              />
              {["1 (Fall)", "2 (Winter/Spring)", "3 (April, 1997–2002)"][r - 1]}
            </label>
          ))}
        </span>
        <label>
          <input
            type="checkbox"
            checked={filters.solutionsOnly}
            onChange={(e) => set({ solutionsOnly: e.target.checked })}
          />
          Only problems with published solutions
        </label>
      </div>
    </div>
  );
}
