import { useState } from "react";

import type { Recommendation } from "../../types";
import { ScoreBreakdownPanel } from "./ScoreBreakdownPanel";

export function AlternativeCard({ recommendation }: { recommendation: Recommendation }) {
  const { elective, match_percent, score_breakdown } = recommendation;
  const [showBreakdown, setShowBreakdown] = useState(false);

  return (
    <div className="border-2 border-ink bg-white p-4">
      <div className="mb-2 flex items-center justify-between">
        <button
          type="button"
          onClick={() => setShowBreakdown((v) => !v)}
          className="font-mono text-xs font-bold text-moss"
          title="Show how this percentage was calculated"
        >
          {match_percent}% Match {showBreakdown ? "▲" : "▼"}
        </button>
        <span className="label-tag text-ink/40">{elective.credits.toFixed(1)} Cr</span>
      </div>
      {showBreakdown && <ScoreBreakdownPanel breakdown={score_breakdown} matchPercent={match_percent} />}
      <p className="font-serif text-base font-bold leading-tight text-ink">{elective.code}</p>
      <p className="text-sm text-ink/70">{elective.title}</p>
      <p className="label-tag mt-2 text-ink/40">{elective.department}</p>
    </div>
  );
}
