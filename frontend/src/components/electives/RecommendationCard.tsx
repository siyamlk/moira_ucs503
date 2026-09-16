import { useState } from "react";

import type { Recommendation } from "../../types";
import { FacultyMiniCard } from "../faculty/FacultyMiniCard";
import { ScoreBreakdownPanel } from "./ScoreBreakdownPanel";

export function RecommendationCard({ recommendation }: { recommendation: Recommendation }) {
  const {
    elective,
    match_percent,
    matched_topics,
    explanation,
    interest_match,
    career_match,
    score_breakdown,
    suggested_faculty,
  } = recommendation;
  const [showSyllabus, setShowSyllabus] = useState(false);
  const [showBreakdown, setShowBreakdown] = useState(false);

  return (
    <div className="card-plate p-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2 border-b-2 border-ink pb-4">
        <span className="label-tag bg-ink px-2 py-1 text-parchment">
          #1 Top Recommendation &middot; {elective.department}
        </span>
        <button
          type="button"
          onClick={() => setShowBreakdown((v) => !v)}
          className="inline-flex items-center gap-1.5 font-mono text-sm font-bold text-moss"
          title="Show how this percentage was calculated"
        >
          <span className="h-2 w-2 rounded-full bg-moss" />
          {match_percent}% Match {showBreakdown ? "▲" : "▼"}
        </button>
      </div>

      {showBreakdown && <ScoreBreakdownPanel breakdown={score_breakdown} matchPercent={match_percent} />}

      <h3 className="font-serif text-2xl font-bold text-ink">
        {elective.code}: {elective.title}
      </h3>
      <p className="mt-1 text-sm text-ink/60">
        {elective.category} &middot; {elective.credits.toFixed(1)} Credits
        {elective.prerequisites && <> &middot; Prerequisites: {elective.prerequisites}</>}
      </p>
      {elective.description && <p className="mt-3 text-sm leading-relaxed text-ink/70">{elective.description}</p>}

      <p className="label-tag mt-5 mb-2 text-ink/50">Why this course fits your profile</p>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div className="border-2 border-ink/30 p-3">
          <p className="label-tag text-ink/50">01 / Interest Match</p>
          <p className="mt-1 text-sm text-ink">
            {interest_match ? `Matches: ${matched_topics.join(", ")}` : "No direct interest overlap."}
          </p>
        </div>
        <div className="border-2 border-ink/30 p-3">
          <p className="label-tag text-ink/50">02 / Career Alignment</p>
          <p className="mt-1 text-sm text-ink">
            {career_match ? "Aligns with your stated career goal." : "No direct career-goal overlap."}
          </p>
        </div>
      </div>

      <div className="sticky-note mt-4">&ldquo;{explanation}&rdquo;</div>

      {suggested_faculty.length > 0 && (
        <div className="mt-5">
          <p className="label-tag mb-2 text-ink/50">Faculty working in this area</p>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {suggested_faculty.map((f) => (
              <FacultyMiniCard key={f.id} faculty={f} />
            ))}
          </div>
        </div>
      )}

      {showSyllabus && (
        <div className="mt-5 border-2 border-ink/30 p-4">
          <p className="label-tag mb-2 text-ink/50">Syllabus Outline</p>
          {elective.syllabus_outline.length > 0 ? (
            <ol className="list-decimal space-y-1 pl-5 text-sm text-ink/80">
              {elective.syllabus_outline.map((unit) => (
                <li key={unit}>{unit}</li>
              ))}
            </ol>
          ) : (
            <p className="text-sm text-ink/50">
              Detailed unit-wise syllabus isn&apos;t available for this course yet.
            </p>
          )}
        </div>
      )}

      <div className="mt-6 flex gap-3">
        <button
          type="button"
          className="btn-outline"
          onClick={() => setShowSyllabus((v) => !v)}
          disabled={elective.syllabus_outline.length === 0}
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
