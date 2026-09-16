import type { MatchBreakdown } from "../../types/recommendation";

/**
 * Renders the scoring engine's actual component breakdown — every row
 * here is a value returned by the backend (app/recommendation/scoring_engine.py),
 * never a value computed or guessed in the frontend. The rows always sum
 * to match_percentage, which is the point: nothing about this number is
 * hidden or fabricated.
 */
export function MatchBreakdownPanel({ breakdown }: { breakdown: MatchBreakdown }) {
  const sum = breakdown.components.reduce((t, c) => t + c.earned, 0);
  return (
    <div className="border-2 border-ink/30 bg-parchmentDark/40 p-3 font-mono text-xs">
      <p className="label-tag mb-2 text-ink/50">Why this percentage? &middot; live-computed, not fixed</p>
      <ul className="space-y-1.5">
        {breakdown.components.map((c) => (
          <li key={c.key} className="flex items-center justify-between gap-2 text-ink/80">
            <span>{c.label}</span>
            <span className="flex items-center gap-2">
              <span className="h-1.5 w-20 overflow-hidden rounded-full bg-ink/10">
                <span
                  className="block h-full rounded-full bg-moss"
                  style={{ width: `${c.max ? (c.earned / c.max) * 100 : 0}%` }}
                />
              </span>
              <span className="whitespace-nowrap font-bold text-ink">
                {c.earned}/{c.max}
              </span>
            </span>
          </li>
        ))}
      </ul>
      <div className="mt-2 flex items-center justify-between border-t border-ink/20 pt-2 text-ink">
        <span>Total</span>
        <span className="font-bold">
          {sum}/{breakdown.max_total} &rarr; {breakdown.total}%
        </span>
      </div>
    </div>
  );
}
