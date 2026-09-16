import { useMemo, useState } from "react";

import type { BasketRecommendation } from "../../types/recommendation";

type SortKey = "match_desc" | "match_asc" | "name_asc";

export function AllBasketsList({
  baskets,
  selectedNames,
  onToggleCompare,
  onOpenBasket,
}: {
  baskets: BasketRecommendation[];
  selectedNames: string[];
  onToggleCompare: (name: string) => void;
  onOpenBasket: (basket: BasketRecommendation) => void;
}) {
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("match_desc");

  const filtered = useMemo(() => {
    let result = baskets;
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      result = result.filter((b) => b.basket_name.toLowerCase().includes(q));
    }
    const sorted = [...result];
    if (sortKey === "match_desc") sorted.sort((a, b) => b.match_percentage - a.match_percentage);
    if (sortKey === "match_asc") sorted.sort((a, b) => a.match_percentage - b.match_percentage);
    if (sortKey === "name_asc") sorted.sort((a, b) => a.basket_name.localeCompare(b.basket_name));
    return sorted;
  }, [baskets, search, sortKey]);

  return (
    <div className="card-plate p-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-serif text-xl font-bold text-ink">Explore Elective Focuses ({baskets.length})</h3>
        <p className="label-tag text-ink/50">Every basket you're eligible for — nothing is hidden.</p>
      </div>

      <div className="mb-4 flex flex-wrap gap-3">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search baskets..."
          className="field-input max-w-xs flex-1"
        />
        <select value={sortKey} onChange={(e) => setSortKey(e.target.value as SortKey)} className="field-input w-auto">
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
              <th className="p-2">Elective Focus / Basket</th>
              <th className="p-2">Match %</th>
              <th className="p-2">Electives</th>
              <th className="p-2" />
            </tr>
          </thead>
          <tbody>
            {filtered.map((b) => (
              <tr key={b.basket_name} className="border-b border-ink/15 align-top">
                <td className="p-2">
                  <input
                    type="checkbox"
                    checked={selectedNames.includes(b.basket_name)}
                    onChange={() => onToggleCompare(b.basket_name)}
                    aria-label={`Select ${b.basket_name} for comparison`}
                  />
                </td>
                <td className="p-2 font-medium text-ink">{b.basket_name}</td>
                <td className="p-2 font-mono font-bold text-moss">{b.match_percentage}%</td>
                <td className="p-2 text-xs text-ink/60">
                  {b.electives.map((e) => e.course_code).join(", ")}
                </td>
                <td className="p-2">
                  <button type="button" onClick={() => onOpenBasket(b)} className="label-tag text-moss underline">
                    Details
                  </button>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={5} className="p-4 text-center text-ink/50">
                  No baskets match your search.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
