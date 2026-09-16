import { useEffect } from "react";

import type { BasketRecommendation } from "../../types/recommendation";

interface BasketDetailModalProps {
  basket: BasketRecommendation;
  isPrimary: boolean;
  primaryMatchPercentage?: number;
  onClose: () => void;
  onOpenElective: (code: string) => void;
}

export function BasketDetailModal({
  basket,
  isPrimary,
  primaryMatchPercentage,
  onClose,
  onOpenElective,
}: BasketDetailModalProps) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const gapToPrimary =
    !isPrimary && primaryMatchPercentage !== undefined ? primaryMatchPercentage - basket.match_percentage : null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-ink/50 p-4 py-10"
      onClick={onClose}
    >
      <div
        className="card-plate w-full max-w-2xl bg-parchment p-6 sm:p-8"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <div className="mb-4 flex items-start justify-between gap-4 border-b-2 border-ink pb-4">
          <div>
            <span className="label-tag text-ink/50">Elective Focus Basket</span>
            <h2 className="mt-1 font-serif text-2xl font-bold text-ink">{basket.basket_name}</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex h-8 w-8 shrink-0 items-center justify-center border-2 border-ink text-ink hover:bg-ink hover:text-parchment"
            aria-label="Close"
          >
            &times;
          </button>
        </div>

        <div className="mb-4 flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 font-mono text-lg font-bold text-moss">
            <span className="h-2.5 w-2.5 rounded-full bg-moss" />
            {basket.match_percentage}% Match
          </span>
          {gapToPrimary !== null && gapToPrimary > 0 && (
            <span className="label-tag text-clay">{gapToPrimary} pts below your recommended basket</span>
          )}
        </div>

        <div className="sticky-note">&ldquo;{basket.why_this_basket_matches}&rdquo;</div>

        {(basket.matched_interests.length > 0 || basket.matched_career_goals.length > 0) && (
          <div className="mt-4 flex flex-wrap gap-2">
            {basket.matched_interests.map((t) => (
              <span key={`i-${t}`} className="chip chip-idle cursor-default border-moss text-moss">
                Interest: {t}
              </span>
            ))}
            {basket.matched_career_goals.map((t) => (
              <span key={`c-${t}`} className="chip chip-idle cursor-default border-clay text-clay">
                Career: {t}
              </span>
            ))}
          </div>
        )}

        <p className="label-tag mt-5 mb-2 text-ink/50">
          Elective I-IV in this basket ({basket.electives.length})
        </p>
        <div className="space-y-2">
          {basket.electives.map((e) => (
            <button
              key={e.course_code}
              type="button"
              onClick={() => onOpenElective(e.course_code)}
              className="flex w-full items-start justify-between gap-3 border-2 border-ink/20 p-3 text-left hover:border-ink"
            >
              <div>
                <span className="label-tag text-ink/40">{e.elective.category}</span>
                <p className="font-serif text-base font-bold text-ink">{e.course_name}</p>
                <p className="font-mono text-xs text-ink/40">{e.course_code}</p>
                <p className="mt-1 text-xs text-ink/60">{e.why_this_matches}</p>
              </div>
              <span className="shrink-0 font-mono text-sm font-bold text-moss">{e.match_percentage}%</span>
            </button>
          ))}
        </div>

        {!isPrimary && (
          <div className="mt-5 border-2 border-ink/30 p-3 text-sm text-ink/70">
            This basket scored lower than your recommended one primarily where its member courses'
            individual match percentages (above) are weaker — open one to see its own breakdown.
          </div>
        )}
      </div>
    </div>
  );
}
