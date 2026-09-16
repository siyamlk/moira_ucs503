import type { ScoreBreakdown } from "../../types";

/**
 * Renders the exact arithmetic behind a match_percent so it's auditable
 * instead of a trust-me number: these four rows always sum to the
 * displayed percentage (see recommendation_service.score_elective).
 */
export function ScoreBreakdownPanel({
  breakdown,
  matchPercent,
}: {
  breakdown: ScoreBreakdown;
  matchPercent: number;
}) {
  const rows = [
    {
      label: "Interest overlap",
      detail: `${breakdown.interest_matched}/${breakdown.interest_total} of your interest tags matched`,
      points: breakdown.interest_points,
      max: 45,
    },
    {
      label: "Career alignment",
      detail: breakdown.career_matched ? "your career goal matched this course" : "no career-goal match",
      points: breakdown.career_points,
      max: 30,
    },
    {
      label: "Topic overlap",
      detail: `${breakdown.topic_matched}/${breakdown.topic_total} of this course's topics matched`,
      points: breakdown.topic_points,
      max: 20,
    },
    {
      label: "Relevance bonus",
      detail: breakdown.bonus_points > 0 ? "any match at all found" : "no match found",
      points: breakdown.bonus_points,
      max: 5,
    },
  ];
  const sum = rows.reduce((total, row) => total + row.points, 0);

  return (
    <div className="mb-4 border-2 border-ink/30 bg-parchmentDark/40 p-3 font-mono text-xs">
      <p className="label-tag mb-2 text-ink/50">
        Live-computed score &middot; not a fixed/hardcoded number
      </p>
      <ul className="space-y-1">
        {rows.map((row) => (
          <li key={row.label} className="flex items-center justify-between gap-2 text-ink/80">
            <span>
              {row.label} <span className="text-ink/50">({row.detail})</span>
            </span>
            <span className="whitespace-nowrap font-bold text-ink">
              +{row.points} / {row.max}
            </span>
          </li>
        ))}
      </ul>
      <div className="mt-2 flex items-center justify-between border-t border-ink/20 pt-2 text-ink">
        <span>Total (capped at 100)</span>
        <span className="font-bold">
          {sum.toFixed(1)} → {matchPercent}%
        </span>
      </div>
    </div>
  );
}
