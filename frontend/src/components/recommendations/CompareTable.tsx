import type { ReactNode } from "react";

import type { AllEligibleItem } from "../../types/recommendation";

function componentValue(item: AllEligibleItem, key: string): string {
  const c = item.score_breakdown.components.find((comp) => comp.key === key);
  return c ? `${c.earned}/${c.max}` : "-";
}

export function CompareTable({ items, onRemove }: { items: AllEligibleItem[]; onRemove: (code: string) => void }) {
  if (items.length === 0) return null;

  const rows: { label: string; render: (item: AllEligibleItem) => ReactNode }[] = [
    { label: "Match %", render: (i) => <span className="font-mono font-bold text-moss">{i.match_percentage}%</span> },
    { label: "Interest Alignment", render: (i) => componentValue(i, "interest") },
    { label: "Career Alignment", render: (i) => componentValue(i, "career") },
    { label: "Syllabus Alignment", render: (i) => componentValue(i, "syllabus") },
    { label: "Skill Alignment", render: (i) => componentValue(i, "skill") },
    { label: "Academic Fit", render: (i) => componentValue(i, "academic") },
    { label: "Prerequisite Compatibility", render: (i) => componentValue(i, "prerequisite") },
    { label: "Matched Topics", render: (i) => i.matched_syllabus_topics.join("; ") || "—" },
    { label: "Matched Skills", render: (i) => i.matched_skills.join(", ") || "—" },
    { label: "Prerequisites", render: (i) => i.elective.prerequisites || "None listed" },
    { label: "Credits", render: (i) => i.elective.credits.toFixed(1) },
    { label: "Slot / Category", render: (i) => i.elective.category },
  ];

  return (
    <div className="card-plate p-6">
      <h3 className="mb-4 font-serif text-xl font-bold text-ink">Compare Electives</h3>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b-2 border-ink text-left">
              <th className="p-2">Factor</th>
              {items.map((item) => (
                <th key={item.course_code} className="p-2 align-top">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-serif text-base font-bold text-ink">{item.course_name}</p>
                      <p className="label-tag text-ink/40">{item.course_code}</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => onRemove(item.course_code)}
                      className="label-tag text-clay"
                      aria-label={`Remove ${item.course_name} from comparison`}
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
                {items.map((item) => (
                  <td key={item.course_code} className="p-2 text-ink">
                    {row.render(item)}
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
