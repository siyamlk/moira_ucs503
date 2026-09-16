import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { AlternativeCard } from "../../components/electives/AlternativeCard";
import { RecommendationCard } from "../../components/electives/RecommendationCard";
import { ChipSelect } from "../../components/forms/ChipSelect";
import { ErrorBanner } from "../../components/common/ErrorBanner";
import { LoadingState } from "../../components/common/LoadingState";
import { PlateTag } from "../../components/common/PlateTag";
import { profileService } from "../../services/profileService";
import { getApiErrorMessage } from "../../services/api";
import { electiveService } from "../../services/electiveService";
import type { RecommendResponse } from "../../types";
import { CAREER_GOALS, INTEREST_TAGS } from "../../utils/tags";

const SAMPLE_PROMPT =
  "I enjoy AI, data analysis, and programming, and I want to work in healthcare predictive systems and autonomous systems. I also need to clear my multivariable calculus backlog this semester.";

export function ElectivesPage() {
  const [freeText, setFreeText] = useState("");
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [careerGoal, setCareerGoal] = useState("");
  const [branch, setBranch] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RecommendResponse | null>(null);

  useEffect(() => {
    profileService
      .get()
      .then((profile) => {
        setSelectedInterests(profile.interests);
        setCareerGoal(profile.career_goal);
        setFreeText(profile.raw_intent_text);
        setBranch(profile.branch);
      })
      .catch(() => {
        /* no existing profile data yet — fine to start blank */
      });
  }, []);

  function toggleInterest(tag: string) {
    setSelectedInterests((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  }

  function toggleCareer(goal: string) {
    setCareerGoal((prev) => (prev === goal ? "" : goal));
  }

  async function handleSubmit() {
    setError(null);
    setIsSubmitting(true);
    try {
      const response = await electiveService.recommend({
        free_text: freeText,
        interests: selectedInterests,
        career_goal: careerGoal,
      });
      setResult(response);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex flex-col gap-8">
      <div className="card-plate p-6 sm:p-8">
        <PlateTag>Plate No. 02 &middot; Elective Advisor</PlateTag>
        <h1 className="mt-4 font-serif text-3xl font-bold text-ink sm:text-4xl">
          What are you curious about?
        </h1>
        <p className="mt-2 max-w-2xl text-ink/70">
          Every choice draws a path. Pin your interests, pick a career direction, and tell MOIRA
          more in your own words — we&apos;ll turn it into ranked, explainable elective
          recommendations.
        </p>

        {branch ? (
          <p className="label-tag mt-3 text-moss">
            Showing electives for {branch} + open electives.{" "}
            <Link to="/profile" className="underline">
              Change branch
            </Link>
          </p>
        ) : (
          <p className="label-tag mt-3 text-clay">
            No branch set — showing electives from all branches.{" "}
            <Link to="/profile" className="underline">
              Set your branch
            </Link>{" "}
            for recommendations scoped to your own program.
          </p>
        )}

        <div className="mt-6">
          <p className="label-tag mb-2 text-ink/50">Step 01 &middot; Pin your academic passions</p>
          <ChipSelect options={INTEREST_TAGS} selected={selectedInterests} onToggle={toggleInterest} />
        </div>

        <div className="mt-6">
          <p className="label-tag mb-2 text-ink/50">Step 02 &middot; Where do you want to go?</p>
          <ChipSelect
            options={CAREER_GOALS}
            selected={careerGoal ? [careerGoal] : []}
            onToggle={toggleCareer}
          />
        </div>

        <div className="mt-6">
          <div className="mb-2 flex items-center justify-between">
            <label htmlFor="intent" className="label-tag text-ink/50">
              Tell MOIRA more (natural language)
            </label>
            <button
              type="button"
              className="label-tag text-moss underline"
              onClick={() => setFreeText(SAMPLE_PROMPT)}
            >
              &#8635; Reset to sample prompt
            </button>
          </div>
          <textarea
            id="intent"
            className="field-input min-h-[110px] resize-y"
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

        <button
          type="button"
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="btn-primary mt-6"
        >
          {isSubmitting ? "Mapping your path..." : "Map My Path →"}
        </button>
      </div>

      {isSubmitting && <LoadingState label="Scoring electives against your profile..." />}

      {result && (
        <div>
          {result.interpreted_tags.length > 0 && (
            <div className="mb-6 flex flex-wrap items-center gap-2">
              <span className="label-tag text-ink/50">Interpreted tags:</span>
              {result.interpreted_tags.map((tag) => (
                <span key={tag} className="chip chip-idle cursor-default border-moss text-moss">
                  {tag}
                </span>
              ))}
            </div>
          )}

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-[2fr_1fr]">
            {result.top_recommendation ? (
              <RecommendationCard recommendation={result.top_recommendation} />
            ) : (
              <div className="card-plate p-6 text-ink/60">
                No electives matched yet — try adding a few more interests or a career goal.
              </div>
            )}

            <div className="flex flex-col gap-3">
              <p className="label-tag text-ink/50">Alternative Pathways</p>
              {result.alternatives.map((alt) => (
                <AlternativeCard key={alt.elective.id} recommendation={alt} />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
