import { PriorityBadge } from "../common/Badge";
import type { PrioritizedBacklog } from "../../types";

export function PrioritizedBacklogRow({ item }: { item: PrioritizedBacklog }) {
  const { backlog, priority_rank, priority_label, cgpa_impact, estimated_new_cgpa, explanation } = item;
  return (
    <div className="border-2 border-ink bg-white p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <span className="flex h-8 w-8 items-center justify-center border-2 border-ink font-mono text-sm font-bold text-ink">
            {String(priority_rank).padStart(2, "0")}
          </span>
          <div>
            <p className="font-serif text-lg font-bold leading-tight text-ink">{backlog.subject}</p>
            <p className="label-tag text-ink/50">
              {backlog.course_code} &middot; {backlog.credits.toFixed(1)} Credits &middot; {backlog.course_type}
            </p>
          </div>
        </div>
        <PriorityBadge label={priority_label} />
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-4 border-t border-ink/20 pt-3 text-sm">
        <span className="font-mono font-bold text-ink">
          CGPA impact: {cgpa_impact > 0 ? "+" : ""}
          {cgpa_impact.toFixed(3)}
        </span>
        <span className="text-ink/60">Estimated new CGPA: {estimated_new_cgpa.toFixed(3)}</span>
      </div>
      <p className="mt-2 text-sm text-ink/70">{explanation}</p>
    </div>
  );
}
