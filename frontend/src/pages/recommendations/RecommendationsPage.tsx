import { useEffect, useMemo, useState } from "react";

import { ChipSelect } from "../../components/forms/ChipSelect";
import { TagListInput } from "../../components/forms/TagListInput";
import { ErrorBanner } from "../../components/common/ErrorBanner";
import { WarningBanner } from "../../components/common/WarningBanner";
import { LoadingState } from "../../components/common/LoadingState";
import { PlateTag } from "../../components/common/PlateTag";
import { AlternativeCourseCard } from "../../components/recommendations/AlternativeCourseCard";
import { AllEligibleList } from "../../components/recommendations/AllEligibleList";
import { AllBasketsList } from "../../components/recommendations/AllBasketsList";
import { AlternativeBasketCard, PrimaryBasketCard } from "../../components/recommendations/BasketCard";
import { BasketCompareTable } from "../../components/recommendations/BasketCompareTable";
import { BasketDetailModal } from "../../components/recommendations/BasketDetailModal";
import { CompareTable } from "../../components/recommendations/CompareTable";
import { CourseDetailModal } from "../../components/recommendations/CourseDetailModal";
import { getApiErrorMessage } from "../../services/api";
import { profileService } from "../../services/profileService";
import { recommendationService } from "../../services/recommendationService";
import type { BasketRecommendation, RecommendationApiResponse, RecommendationItem } from "../../types/recommendation";
import { CAREER_GOALS, INTEREST_TAGS } from "../../utils/tags";

const ELECTIVE_SLOTS = ["Elective I", "Elective II", "Elective III", "Elective IV", "Generic Elective"];
const CAREER_PREFERENCES = ["Research", "Industry", "Higher Studies", "Entrepreneurship"];
// Mirrors backend/app/seed/seed_data.py CODE_TO_BASKET — every named EFB
// track. A student takes Elective I-IV from ONE of these only.
const EFB_BASKETS = [
  "High Performance Computing",
  "Computer Animation and Gaming",
  "Information and Cyber Security",
  "Mathematics and Computing",
  "Data Science",
  "Financial Derivative",
  "DevOps and Continuous Delivery",
  "Full Stack",
  "Conversational AI",
  "Robotics and Edge AI",
  "Cyber Forensics and Ethical Hacking",
];

const SAMPLE_PROMPT =
  "I want to work with large language models and NLP after graduating, and I'm also curious about generative AI.";

export function RecommendationsPage() {
  const [interests, setInterests] = useState<string[]>([]);
  const [careerGoals, setCareerGoals] = useState<string[]>([]);
  const [skills, setSkills] = useState<string[]>([]);
  const [completedCourses, setCompletedCourses] = useState<string[]>([]);
  const [careerPreference, setCareerPreference] = useState("");
  const [electiveSlot, setElectiveSlot] = useState("");
  const [currentBasket, setCurrentBasket] = useState("");
  const [freeText, setFreeText] = useState("");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RecommendationApiResponse | null>(null);

  const [openDetailsCode, setOpenDetailsCode] = useState<string | null>(null);
  const [openBasketItem, setOpenBasketItem] = useState<RecommendationItem | null>(null);
  const [openAltBasket, setOpenAltBasket] = useState<BasketRecommendation | null>(null);
  const [compareCodes, setCompareCodes] = useState<string[]>([]);
  const [compareBasketNames, setCompareBasketNames] = useState<string[]>([]);

  useEffect(() => {
    profileService
      .get()
      .then((profile) => {
        // Defensive: an account whose profile predates a given field (e.g.
        // skills/completed_courses added after they signed up) can come
        // back with that field missing rather than an empty array/string.
        setInterests(profile.interests ?? []);
        setCareerGoals(profile.career_goal ? [profile.career_goal] : []);
        setSkills(profile.skills ?? []);
        setCompletedCourses(profile.completed_courses ?? []);
        setCareerPreference(profile.career_preference ?? "");
        setCurrentBasket(profile.current_basket ?? "");
        setFreeText(profile.raw_intent_text ?? "");
      })
      .catch(() => {
        /* no profile yet — fine to start blank */
      });
  }, []);

  function toggleInterest(tag: string) {
    setInterests((prev) => (prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]));
  }

  function toggleCareerGoal(goal: string) {
    setCareerGoals((prev) => (prev.includes(goal) ? prev.filter((g) => g !== goal) : [...prev, goal]));
  }

  async function handleSubmit() {
    setError(null);
    setIsSubmitting(true);
    setCompareCodes([]);
    setCompareBasketNames([]);
    try {
      const response = await recommendationService.recommend({
        student_profile: {
          interests,
          career_goals: careerGoals,
          skills,
          completed_courses: completedCourses,
          career_preference: careerPreference,
          free_text: freeText,
          current_basket: currentBasket,
        },
        elective_slot: electiveSlot || null,
      });
      setResult(response);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  const allEligible = result?.all_eligible_courses ?? [];
  const openItem = useMemo(
    () => allEligible.find((c) => c.course_code === openDetailsCode) ?? null,
    [allEligible, openDetailsCode]
  );
  const compareItems = useMemo(
    () => allEligible.filter((c) => compareCodes.includes(c.course_code)),
    [allEligible, compareCodes]
  );

  function toggleCompare(code: string) {
    setCompareCodes((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : prev.length < 4 ? [...prev, code] : prev
    );
  }

  const allBaskets = result?.all_baskets ?? [];
  const compareBaskets = useMemo(
    () => allBaskets.filter((b) => compareBasketNames.includes(b.basket_name)),
    [allBaskets, compareBasketNames]
  );

  function toggleCompareBasket(name: string) {
    setCompareBasketNames((prev) =>
      prev.includes(name) ? prev.filter((n) => n !== name) : prev.length < 3 ? [...prev, name] : prev
    );
  }

  return (
    <div className="flex flex-col gap-8">
      <div className="card-plate p-6 sm:p-8">
        <PlateTag>Elective Advisor &middot; Recommendation Engine</PlateTag>
        <h1 className="mt-4 font-serif text-3xl font-bold text-ink sm:text-4xl">Tell your Elective Advisor about you.</h1>
        <p className="mt-2 max-w-2xl text-ink/70">
          Every match below is computed live from your profile against the real EFB elective syllabus data —
          nothing is a fixed number, and you can always see exactly why.
        </p>

        <div className="mt-6">
          <p className="label-tag mb-2 text-ink/50">Step 01 &middot; Academic / technical interests</p>
          <ChipSelect
            options={INTEREST_TAGS}
            selected={interests.filter((i) => INTEREST_TAGS.includes(i))}
            onToggle={toggleInterest}
          />
          <div className="mt-3">
            <TagListInput
              label="Not on the list? Add your own"
              values={interests.filter((i) => !INTEREST_TAGS.includes(i))}
              onChange={(customValues) =>
                setInterests([...interests.filter((i) => INTEREST_TAGS.includes(i)), ...customValues])
              }
              placeholder="e.g. Sustainable Computing, Quantum Computing..."
              helpText="Matched literally against course titles, descriptions and syllabus text — real evidence only, not guessed."
            />
          </div>
        </div>

        <div className="mt-6">
          <p className="label-tag mb-2 text-ink/50">Step 02 &middot; Career goal(s) — pick one or more</p>
          <ChipSelect options={CAREER_GOALS} selected={careerGoals} onToggle={toggleCareerGoal} />
        </div>

        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <TagListInput
            label="Skills / technologies you know"
            values={skills}
            onChange={setSkills}
            placeholder="e.g. Docker, PyTorch, React..."
            helpText="Press Enter or comma to add. Matched literally against course syllabus text."
          />
          <TagListInput
            label="Courses you've already completed"
            values={completedCourses}
            onChange={setCompletedCourses}
            placeholder="e.g. Finance, Accounting and Valuation..."
            helpText="Used for prerequisite compatibility and academic fit."
          />
        </div>

        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="elective-slot" className="label-tag mb-1.5 block text-ink">
              Elective slot you're choosing from
            </label>
            <select
              id="elective-slot"
              className="field-input"
              value={electiveSlot}
              onChange={(e) => setElectiveSlot(e.target.value)}
            >
              <option value="">Any slot (no filter)</option>
              {ELECTIVE_SLOTS.map((slot) => (
                <option key={slot} value={slot}>
                  {slot}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="career-pref" className="label-tag mb-1.5 block text-ink">
              Preference (optional)
            </label>
            <select
              id="career-pref"
              className="field-input"
              value={careerPreference}
              onChange={(e) => setCareerPreference(e.target.value)}
            >
              <option value="">Not specified</option>
              {CAREER_PREFERENCES.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-6">
          <label htmlFor="current-basket" className="label-tag mb-1.5 block text-ink">
            Elective Focus Basket you've already committed to (leave blank if picking Elective I)
          </label>
          <select
            id="current-basket"
            className="field-input"
            value={currentBasket}
            onChange={(e) => setCurrentBasket(e.target.value)}
          >
            <option value="">Not committed yet — recommend a basket</option>
            {EFB_BASKETS.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-ink/50">
            Elective I-IV all come from one basket only — once you've picked, your remaining choices
            are locked to it.
          </p>
        </div>

        <div className="mt-6">
          <div className="mb-2 flex items-center justify-between">
            <label htmlFor="free-text" className="label-tag text-ink/50">
              Tell your Elective Advisor more (natural language)
            </label>
            <button type="button" className="label-tag text-moss underline" onClick={() => setFreeText(SAMPLE_PROMPT)}>
              &#8635; Reset to sample prompt
            </button>
          </div>
          <textarea
            id="free-text"
            className="field-input min-h-[100px] resize-y"
            placeholder={SAMPLE_PROMPT}
            value={freeText}
            onChange={(e) => setFreeText(e.target.value)}
          />
        </div>

        {error && (
          <div className="mt-4">
            <ErrorBanner message={error} />
          </div>
        )}

        <button type="button" onClick={handleSubmit} disabled={isSubmitting} className="btn-primary mt-6">
          {isSubmitting ? "Analyzing your profile..." : "Get My Recommendations →"}
        </button>
      </div>

      {isSubmitting && <LoadingState label="Scoring every eligible elective against your profile..." />}

      {result && (
        <>
          {result.branch_warning && <WarningBanner message={result.branch_warning} />}

          {(result.interpreted_interests.length > 0 || result.interpreted_career_goals.length > 0) && (
            <div className="flex flex-wrap items-center gap-2">
              <span className="label-tag text-ink/50">Elective Advisor understood:</span>
              {result.interpreted_interests.map((tag) => (
                <span key={`int-${tag}`} className="chip chip-idle cursor-default border-moss text-moss">
                  {tag}
                </span>
              ))}
              {result.interpreted_career_goals.map((tag) => (
                <span key={`car-${tag}`} className="chip chip-idle cursor-default border-clay text-clay">
                  {tag}
                </span>
              ))}
              {result.elective_slot && (
                <span className="chip chip-idle cursor-default">Slot: {result.elective_slot}</span>
              )}
            </div>
          )}

          {result.primary_basket ? (
            <PrimaryBasketCard
              basket={result.primary_basket}
              onOpenElective={(code) => {
                const item = result.primary_basket?.electives.find((e) => e.course_code === code) ?? null;
                setOpenBasketItem(item);
              }}
            />
          ) : (
            <div className="card-plate p-6 text-ink/60">
              No eligible Elective Focus Basket matched — try adding a few more interests, or browse
              individual electives below.
            </div>
          )}

          {result.alternative_baskets.length > 0 && (
            <div>
              <p className="label-tag mb-3 text-ink/50">Explore Alternative Elective Focuses</p>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {result.alternative_baskets.map((b) => (
                  <AlternativeBasketCard key={b.basket_name} basket={b} onOpen={() => setOpenAltBasket(b)} />
                ))}
              </div>
            </div>
          )}

          <AllBasketsList
            baskets={result.all_baskets}
            selectedNames={compareBasketNames}
            onToggleCompare={toggleCompareBasket}
            onOpenBasket={setOpenAltBasket}
          />

          <BasketCompareTable baskets={compareBaskets} onRemove={toggleCompareBasket} />

          <div>
            <p className="label-tag mb-3 text-ink/50">
              Browse Individual Electives (including open/generic and non-basket courses)
            </p>
            {result.primary_recommendation && (
              <div className="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {[result.primary_recommendation, ...result.alternatives].map((alt) => (
                  <AlternativeCourseCard
                    key={alt.course_code}
                    item={alt}
                    onOpen={() => setOpenDetailsCode(alt.course_code)}
                  />
                ))}
              </div>
            )}
            <AllEligibleList
              courses={allEligible}
              selectedCodes={compareCodes}
              onToggleCompare={toggleCompare}
              onOpenDetails={setOpenDetailsCode}
            />
            <div className="mt-6">
              <CompareTable items={compareItems} onRemove={toggleCompare} />
            </div>
          </div>
        </>
      )}

      {openItem && (
        <CourseDetailModal
          item={openItem}
          isPrimary={openItem.course_code === result?.primary_recommendation?.course_code}
          primaryMatchPercentage={result?.primary_recommendation?.match_percentage}
          onClose={() => setOpenDetailsCode(null)}
        />
      )}

      {openBasketItem && (
        <CourseDetailModal
          item={openBasketItem}
          isPrimary={openBasketItem.course_code === result?.primary_recommendation?.course_code}
          primaryMatchPercentage={result?.primary_recommendation?.match_percentage}
          onClose={() => setOpenBasketItem(null)}
        />
      )}

      {openAltBasket && (
        <BasketDetailModal
          basket={openAltBasket}
          isPrimary={openAltBasket.basket_name === result?.primary_basket?.basket_name}
          primaryMatchPercentage={result?.primary_basket?.match_percentage}
          onClose={() => setOpenAltBasket(null)}
          onOpenElective={(code) => {
            const item = openAltBasket.electives.find((e) => e.course_code === code) ?? null;
            setOpenAltBasket(null);
            setOpenBasketItem(item);
          }}
        />
      )}
    </div>
  );
}
