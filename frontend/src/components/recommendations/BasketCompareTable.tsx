import type { ReactNode } from "react";

import type { BasketRecommendation } from "../../types/recommendation";

const SLOT_ORDER = ["Elective I", "Elective II", "Elective III", "Elective IV"];

export function BasketCompareTable({
  baskets,
  onRemove,
}: {
  baskets: BasketRecommendation[];
  onRemove: (name: string) => void;
}) {
  if (baskets.length === 0) return null;

  const rows: { label: string; render: (b: BasketRecommendation) => ReactNode }[] = [
    { label: "Match %", render: (b) => <span className="font-mono font-bold text-moss">{b.match_percentage}%</span> },
    { label: "Matched Interests", render: (b) => b.matched_interests.join(", ") || "—" },
    { label: "Matched Career Goals", render: (b) => b.matched_career_goals.join(", ") || "—" },
    { label: "Total Credits", render: (b) => b.electives.reduce((sum, e) => sum + e.elective.credits, 0).toFixed(1) },
    ...SLOT_ORDER.map((slot) => ({
      label: slot,
      render: (b: BasketRecommendation) => {
        const e = b.electives.find((x) => x.elective.category === slot);
        return e ? (
          <span>
            {e.course_name} <span className="text-ink/40">({e.match_percentage}%)</span>
          </span>
        ) : (
          "—"
        );
      },
    })),
  ];

  return (
    <div className="card-plate p-6">
      <h3 className="mb-4 font-serif text-xl font-bold text-ink">Compare Elective Focuses</h3>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b-2 border-ink text-left">
              <th className="p-2">Factor</th>
              {baskets.map((b) => (
                <th key={b.basket_name} className="p-2 align-top">
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-serif text-base font-bold text-ink">{b.basket_name}</p>
                    <button
                      type="button"
                      onClick={() => onRemove(b.basket_name)}
                      className="label-tag text-clay"
                      aria-label={`Remove ${b.basket_name} from comparison`}
                    >
                      Remove
                    </button>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.label} className="border-b border-ink/15">
                <td className="p-2 font-medium text-ink/60">{row.label}</td>
                {baskets.map((b) => (
                  <td key={b.basket_name} className="p-2 text-ink">
                    {row.render(b)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
