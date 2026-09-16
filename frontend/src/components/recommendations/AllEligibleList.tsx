import { useMemo, useState } from "react";

import type { AllEligibleItem } from "../../types/recommendation";

type SortKey = "match_desc" | "match_asc" | "name_asc";

export function AllEligibleList({
  courses,
  selectedCodes,
  onToggleCompare,
  onOpenDetails,
}: {
  courses: AllEligibleItem[];
  selectedCodes: string[];
  onToggleCompare: (code: string) => void;
  onOpenDetails: (code: string) => void;
}) {
  const [search, setSearch] = useState("");
  const [domainFilter, setDomainFilter] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("match_desc");

  const domains = useMemo(
    () => Array.from(new Set(courses.map((c) => c.domain))).sort(),
    [courses]
  );

  const filtered = useMemo(() => {
    let result = courses;
    if (domainFilter) {
      result = result.filter((c) => c.domain === domainFilter);
    }
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      result = result.filter(
        (c) => c.course_name.toLowerCase().includes(q) || c.course_code.toLowerCase().includes(q)
      );
    }
    const sorted = [...result];
    if (sortKey === "match_desc") sorted.sort((a, b) => b.match_percentage - a.match_percentage);
    if (sortKey === "match_asc") sorted.sort((a, b) => a.match_percentage - b.match_percentage);
    if (sortKey === "name_asc") sorted.sort((a, b) => a.course_name.localeCompare(b.course_name));
    return sorted;
  }, [courses, domainFilter, search, sortKey]);

  return (
    <div className="card-plate p-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-serif text-xl font-bold text-ink">All Eligible Electives ({courses.length})</h3>
        <p className="label-tag text-ink/50">Lower scores are never hidden — browse everything you're eligible for.</p>
      </div>

      <div className="mb-4 flex flex-wrap gap-3">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name or code..."
          className="field-input max-w-xs flex-1"
        />
        <select
          value={domainFilter}
          onChange={(e) => setDomainFilter(e.target.value)}
          className="field-input w-auto"
        >
          <option value="">All domains/slots</option>
          {domains.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
        <select
          value={sortKey}
          onChange={(e) => setSortKey(e.target.value as SortKey)}
          className="field-input w-auto"
        >
          <option value="match_desc">Sort: Match % (high to low)</option>
          <option value="match_asc">Sort: Match % (low to high)</option>
          <option value="name_asc">Sort: Name (A-Z)</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b-2 border-ink text-left">
              <th className="p-2">Compare</th>
              <th className="p-2">Course</th>
              <th className="p-2">Code</th>
              <th className="p-2">Domain / Slot</th>
              <th className="p-2">Match %</th>
              <th className="p-2">Why</th>
              <th className="p-2" />
            </tr>
          </thead>
          <tbody>
            {filtered.map((c) => (
              <tr key={`${c.course_code}-${c.domain}`} className="border-b border-ink/15 align-top">
                <td className="p-2">
                  <input
                    type="checkbox"
                    checked={selectedCodes.includes(c.course_code)}
                    onChange={() => onToggleCompare(c.course_code)}
                    aria-label={`Select ${c.course_name} for comparison`}
                  />
                </td>
                <td className="p-2 font-medium text-ink">{c.course_name}</td>
                <td className="p-2 font-mono text-xs text-ink/60">{c.course_code}</td>
                <td className="p-2 text-ink/60">{c.domain}</td>
                <td className="p-2 font-mono font-bold text-moss">{c.match_percentage}%</td>
                <td className="p-2 max-w-xs text-xs text-ink/60">{c.short_reason}</td>
                <td className="p-2">
                  <button
                    type="button"
                    onClick={() => onOpenDetails(c.course_code)}
                    className="label-tag text-moss underline"
                  >
                    Details
                  </button>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={7} className="p-4 text-center text-ink/50">
                  No electives match your search/filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
