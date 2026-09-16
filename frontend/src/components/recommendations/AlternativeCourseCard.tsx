import type { RecommendationItem } from "../../types/recommendation";

export function AlternativeCourseCard({
  item,
  onOpen,
}: {
  item: RecommendationItem;
  onOpen: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onOpen}
      className="card-plate w-full p-4 text-left transition-transform hover:-translate-y-0.5"
    >
      <div className="mb-2 flex items-center justify-between">
        <span className="font-mono text-sm font-bold text-moss">{item.match_percentage}% MATCH</span>
        <span className="label-tag text-ink/40">{item.elective.credits.toFixed(1)} Cr</span>
      </div>
      <p className="font-serif text-lg font-bold leading-tight text-ink">{item.course_name}</p>
      <p className="font-mono text-xs text-ink/50">{item.course_code}</p>
      <p className="mt-2 text-sm text-ink/70">{item.why_this_matches}</p>
      {item.matched_syllabus_topics.length > 0 && (
        <p className="mt-2 text-xs text-ink/50">
          <span className="label-tag text-ink/40">Syllabus: </span>
          {item.matched_syllabus_topics.slice(0, 2).join("; ")}
        </p>
      )}
      <span className="btn-outline mt-3 inline-block !py-1.5 !px-3 text-xs">View Details →</span>
    </button>
  );
}
