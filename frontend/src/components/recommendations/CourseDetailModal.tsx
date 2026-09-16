import { useEffect } from "react";

import type { RecommendationItem } from "../../types/recommendation";
import { MatchBreakdownPanel } from "./MatchBreakdownPanel";

interface CourseDetailModalProps {
  item: RecommendationItem;
  isPrimary: boolean;
  primaryMatchPercentage?: number;
  onClose: () => void;
}

export function CourseDetailModal({ item, isPrimary, primaryMatchPercentage, onClose }: CourseDetailModalProps) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const gapToPrimary =
    !isPrimary && primaryMatchPercentage !== undefined ? primaryMatchPercentage - item.match_percentage : null;

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
            <span className="label-tag text-ink/50">{item.elective.department}</span>
            <h2 className="mt-1 font-serif text-2xl font-bold text-ink">
              {item.course_code}: {item.course_name}
            </h2>
            <p className="mt-1 text-sm text-ink/60">
              {item.elective.category} &middot; {item.elective.credits.toFixed(1)} Credits
            </p>
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
            {item.match_percentage}% Match
          </span>
          {gapToPrimary !== null && gapToPrimary > 0 && (
            <span className="label-tag text-clay">{gapToPrimary} pts below your top match</span>
          )}
        </div>

        <MatchBreakdownPanel breakdown={item.score_breakdown} />

        {item.elective.description && (
          <p className="mt-4 text-sm leading-relaxed text-ink/70">{item.elective.description}</p>
        )}

        <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
          <DetailBlock title="Why this matches you" text={item.why_this_matches} />
          <DetailBlock title="Career relevance" text={item.career_relevance} />
          <DetailBlock title="Syllabus alignment" text={item.syllabus_alignment} />
          <DetailBlock title="Skill alignment" text={item.skill_alignment} />
          <DetailBlock title="Academic / prerequisite context" text={item.academic_context} />
          <DetailBlock title="Prerequisite compatibility" text={item.prerequisite_context} />
        </div>

        {item.elective.syllabus_outline.length > 0 && (
          <div className="mt-5 border-2 border-ink/30 p-4">
            <p className="label-tag mb-2 text-ink/50">Full Syllabus Outline</p>
            <ol className="list-decimal space-y-1 pl-5 text-sm text-ink/80">
              {item.elective.syllabus_outline.map((unit) => (
                <li key={unit}>{unit}</li>
              ))}
            </ol>
          </div>
        )}

        {item.matched_interests.length + item.matched_career_goals.length + item.matched_skills.length > 0 && (
          <div className="mt-5">
            <p className="label-tag mb-2 text-ink/50">What from your profile influenced this</p>
            <div className="flex flex-wrap gap-2">
              {item.matched_interests.map((t) => (
                <span key={`i-${t}`} className="chip chip-idle cursor-default border-moss text-moss">
                  Interest: {t}
                </span>
              ))}
              {item.matched_career_goals.map((t) => (
                <span key={`c-${t}`} className="chip chip-idle cursor-default border-clay text-clay">
                  Career: {t}
                </span>
              ))}
              {item.matched_skills.map((t) => (
                <span key={`s-${t}`} className="chip chip-idle cursor-default">
                  Skill: {t}
                </span>
              ))}
            </div>
          </div>
        )}

        {!isPrimary && (
          <div className="sticky-note mt-5">
            &ldquo;This course scored lower than your top match primarily where its breakdown above shows the
            smallest bars — usually interest, career or syllabus overlap.&rdquo;
          </div>
        )}
      </div>
    </div>
  );
}

function DetailBlock({ title, text }: { title: string; text: string }) {
  return (
    <div className="border-2 border-ink/30 p-3">
      <p className="label-tag text-ink/50">{title}</p>
      <p className="mt-1 text-sm text-ink/80">{text}</p>
    </div>
  );
}
