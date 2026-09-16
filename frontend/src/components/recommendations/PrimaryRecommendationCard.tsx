import { useState } from "react";

import type { RecommendationItem } from "../../types/recommendation";
import { MatchBreakdownPanel } from "./MatchBreakdownPanel";

export function PrimaryRecommendationCard({ item }: { item: RecommendationItem }) {
  const [showBreakdown, setShowBreakdown] = useState(false);
  const [showSyllabus, setShowSyllabus] = useState(false);

  return (
    <div className="card-plate p-6 sm:p-8">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2 border-b-2 border-ink pb-4">
        <span className="label-tag bg-ink px-2 py-1 text-parchment">
          Your Top Match &middot; {item.elective.department}
        </span>
        <button
          type="button"
          onClick={() => setShowBreakdown((v) => !v)}
          className="inline-flex items-center gap-1.5 font-mono text-lg font-bold text-moss"
        >
          <span className="h-2.5 w-2.5 rounded-full bg-moss" />
          {item.match_percentage}% MATCH {showBreakdown ? "▲" : "▼"}
        </button>
      </div>

      {showBreakdown && (
        <div className="mb-5">
          <MatchBreakdownPanel breakdown={item.score_breakdown} />
        </div>
      )}

      <h2 className="font-serif text-3xl font-bold text-ink">{item.course_name}</h2>
      <p className="mt-1 font-mono text-sm text-ink/60">
        {item.course_code} &middot; {item.elective.category} &middot; {item.elective.credits.toFixed(1)} Credits
        {item.elective.prerequisites && <> &middot; Prerequisites: {item.elective.prerequisites}</>}
      </p>

      {item.elective.description && (
        <p className="mt-4 text-sm leading-relaxed text-ink/70">{item.elective.description}</p>
      )}

      <p className="label-tag mt-6 mb-2 text-ink/50">Why this was chosen</p>
      <div className="sticky-note">&ldquo;{item.why_this_matches}&rdquo;</div>

      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <Block title="Career relevance" text={item.career_relevance} />
        <Block title="Syllabus alignment" text={item.syllabus_alignment} />
        <Block title="Skill alignment" text={item.skill_alignment} />
        <Block title="Academic fit" text={item.academic_context} />
      </div>

      {item.prerequisite_context && (
        <div className="mt-3 border-2 border-ink/30 p-3">
          <p className="label-tag text-ink/50">Prerequisite compatibility</p>
          <p className="mt-1 text-sm text-ink/80">{item.prerequisite_context}</p>
        </div>
      )}

      {showSyllabus && item.elective.syllabus_outline.length > 0 && (
        <div className="mt-4 border-2 border-ink/30 p-4">
          <p className="label-tag mb-2 text-ink/50">Full Syllabus Outline</p>
          <ol className="list-decimal space-y-1 pl-5 text-sm text-ink/80">
            {item.elective.syllabus_outline.map((unit) => (
              <li key={unit}>{unit}</li>
            ))}
          </ol>
        </div>
      )}

      <div className="mt-6 flex gap-3">
        <button
          type="button"
          className="btn-outline"
          onClick={() => setShowSyllabus((v) => !v)}
          disabled={item.elective.syllabus_outline.length === 0}
        >
          {showSyllabus ? "Hide Syllabus Outline" : "Syllabus Outline"}
        </button>
        <button type="button" className="btn-primary" disabled title="Enrollment not yet available">
          Enroll on My Map
        </button>
      </div>
    </div>
  );
}

function Block({ title, text }: { title: string; text: string }) {
  return (
    <div className="border-2 border-ink/30 p-3">
      <p className="label-tag text-ink/50">{title}</p>
      <p className="mt-1 text-sm text-ink">{text}</p>
    </div>
  );
}
