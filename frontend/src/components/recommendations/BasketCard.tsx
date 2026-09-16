import type { BasketRecommendation } from "../../types/recommendation";

const SLOT_ORDER = ["Elective I", "Elective II", "Elective III", "Elective IV"];

function BasketElectiveList({
  electives,
  onOpenElective,
}: {
  electives: BasketRecommendation["electives"];
  onOpenElective: (code: string) => void;
}) {
  return (
    <ol className="mt-3 space-y-1.5">
      {electives.map((e) => (
        <li key={e.course_code}>
          <button
            type="button"
            onClick={() => onOpenElective(e.course_code)}
            className="flex w-full items-center justify-between gap-2 border-2 border-ink/20 px-3 py-2 text-left hover:border-ink"
          >
            <span>
              <span className="label-tag text-ink/40">{e.elective.category}</span>
              <span className="ml-2 text-sm font-medium text-ink">{e.course_name}</span>
              <span className="ml-1 font-mono text-xs text-ink/40">{e.course_code}</span>
            </span>
            <span className="font-mono text-sm font-bold text-moss">{e.match_percentage}%</span>
          </button>
        </li>
      ))}
    </ol>
  );
}

export function PrimaryBasketCard({
  basket,
  onOpenElective,
}: {
  basket: BasketRecommendation;
  onOpenElective: (code: string) => void;
}) {
  return (
    <div className="card-plate p-6 sm:p-8">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2 border-b-2 border-ink pb-4">
        <span className="label-tag bg-ink px-2 py-1 text-parchment">Recommended Elective Focus</span>
        <span className="inline-flex items-center gap-1.5 font-mono text-lg font-bold text-moss">
          <span className="h-2.5 w-2.5 rounded-full bg-moss" />
          {basket.match_percentage}% MATCH
        </span>
      </div>
      <h2 className="font-serif text-3xl font-bold text-ink">{basket.basket_name}</h2>
      <p className="mt-2 text-sm text-ink/60">
        A student commits to one Elective Focus Basket and takes Elective I-IV from within it —
        here's how each of this basket's courses matches your profile.
      </p>
      <div className="sticky-note mt-4">&ldquo;{basket.why_this_basket_matches}&rdquo;</div>
      <p className="label-tag mt-5 mb-1 text-ink/50">The four electives in this basket</p>
      <BasketElectiveList electives={basket.electives} onOpenElective={onOpenElective} />
    </div>
  );
}

export function AlternativeBasketCard({
  basket,
  onOpen,
}: {
  basket: BasketRecommendation;
  onOpen: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onOpen}
      className="card-plate w-full p-4 text-left transition-transform hover:-translate-y-0.5"
    >
      <div className="mb-2 flex items-center justify-between">
        <span className="font-mono text-sm font-bold text-moss">{basket.match_percentage}% MATCH</span>
        <span className="label-tag text-ink/40">{basket.electives.length} electives</span>
      </div>
      <p className="font-serif text-lg font-bold leading-tight text-ink">{basket.basket_name}</p>
      <p className="mt-2 text-sm text-ink/70">{basket.why_this_basket_matches}</p>
      <div className="mt-2 flex flex-wrap gap-1">
        {SLOT_ORDER.map((slot) => {
          const e = basket.electives.find((x) => x.elective.category === slot);
          return (
            <span key={slot} className="label-tag border border-ink/20 px-1.5 py-0.5 text-ink/50">
              {e ? `${e.course_code} ${e.match_percentage}%` : `${slot}: —`}
            </span>
          );
        })}
      </div>
      <span className="btn-outline mt-3 inline-block !py-1.5 !px-3 text-xs">View Basket →</span>
    </button>
  );
}
