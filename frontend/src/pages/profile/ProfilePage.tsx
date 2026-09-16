import { useEffect, useState } from "react";

import { ChipSelect } from "../../components/forms/ChipSelect";
import { TextField } from "../../components/forms/TextField";
import { ErrorBanner } from "../../components/common/ErrorBanner";
import { LoadingState } from "../../components/common/LoadingState";
import { PlateTag } from "../../components/common/PlateTag";
import { useAuth } from "../../context/AuthContext";
import { getApiErrorMessage } from "../../services/api";
import { profileService } from "../../services/profileService";
import type { Profile } from "../../types";
import { BRANCHES } from "../../utils/branches";
import { initials } from "../../utils/format";
import { CAREER_GOALS, INTEREST_TAGS } from "../../utils/tags";

export function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedAt, setSavedAt] = useState<number | null>(null);

  useEffect(() => {
    profileService
      .get()
      .then(setProfile)
      .catch((err) => setError(getApiErrorMessage(err)))
      .finally(() => setIsLoading(false));
  }, []);

  function updateField<K extends keyof Profile>(key: K, value: Profile[K]) {
    setProfile((prev) => (prev ? { ...prev, [key]: value } : prev));
  }

  async function handleSave() {
    if (!profile) return;
    setError(null);
    setIsSaving(true);
    try {
      const updated = await profileService.update({
        semester: profile.semester,
        branch: profile.branch,
        cgpa: profile.cgpa,
        credits_earned: profile.credits_earned,
        credits_required: profile.credits_required,
        career_goal: profile.career_goal,
        interests: profile.interests,
      });
      setProfile(updated);
      setSavedAt(Date.now());
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) {
    return <LoadingState label="Opening your notebook..." />;
  }

  if (!profile || !user) {
    return <ErrorBanner message={error ?? "Could not load your profile."} />;
  }

  const progressPct = profile.credits_required
    ? Math.min(100, Math.round((profile.credits_earned / profile.credits_required) * 100))
    : 0;

  return (
    <div className="flex flex-col gap-8">
      <div className="card-plate p-6 sm:p-8">
        <PlateTag>Student Archive &middot; My Moira Notebook</PlateTag>
        <h1 className="mt-4 font-serif text-3xl font-bold text-ink sm:text-4xl">The Open Notebook</h1>
        <p className="mt-2 max-w-2xl text-ink/70">
          Your academic profile, interests, goals and backlogs — the context MOIRA uses for every
          recommendation.
        </p>
      </div>

      {error && <ErrorBanner message={error} />}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="card-plate flex flex-col gap-4 p-6">
          <div className="flex items-center gap-3">
            <span className="flex h-14 w-14 items-center justify-center border-2 border-ink bg-ink font-serif text-xl font-bold text-parchment">
              {initials(user.full_name)}
            </span>
            <div>
              <p className="font-serif text-lg font-bold text-ink">{user.full_name}</p>
              <p className="label-tag text-ink/50">
                {user.student_id} &middot; Sem {profile.semester}
              </p>
            </div>
          </div>

          <div className="border-2 border-ink/20 p-3">
            <p className="label-tag text-ink/50">Current CGPA</p>
            <p className="font-serif text-3xl font-bold text-ink">{profile.cgpa.toFixed(2)} / 10.0</p>
          </div>

          <div className="border-2 border-ink/20 p-3">
            <div className="mb-1 flex justify-between text-sm">
              <span className="label-tag text-ink/50">Credits Earned</span>
              <span className="font-mono font-bold text-ink">
                {profile.credits_earned} / {profile.credits_required} ({progressPct}%)
              </span>
            </div>
            <div className="h-2 w-full border border-ink bg-parchmentDark">
              <div className="h-full bg-moss" style={{ width: `${progressPct}%` }} />
            </div>
          </div>

          <div className="sticky-note text-base">
            &ldquo;Your academic profile helps MOIRA understand the paths that fit you.&rdquo;
          </div>
        </div>

        <div className="card-plate flex flex-col gap-4 p-6 lg:col-span-2">
          <p className="label-tag text-ink/50">Academic Details</p>
          <div className="grid grid-cols-2 gap-4">
            <TextField
              label="Semester"
              type="number"
              min={1}
              max={12}
              value={profile.semester}
              onChange={(e) => updateField("semester", Number(e.target.value))}
            />
            <TextField
              label="CGPA"
              type="number"
              step="0.01"
              min={0}
              max={10}
              value={profile.cgpa}
              onChange={(e) => updateField("cgpa", Number(e.target.value))}
            />
            <TextField
              label="Credits Earned"
              type="number"
              min={0}
              value={profile.credits_earned}
              onChange={(e) => updateField("credits_earned", Number(e.target.value))}
            />
            <TextField
              label="Credits Required"
              type="number"
              min={0}
              value={profile.credits_required}
              onChange={(e) => updateField("credits_required", Number(e.target.value))}
            />
          </div>
          <div>
            <div className="mb-1.5 flex items-baseline justify-between">
              <label htmlFor="branch" className="label-tag text-ink">
                Branch
              </label>
              <span className="label-tag text-ink/40">Determines which electives you see</span>
            </div>
            <select
              id="branch"
              className="field-input"
              value={profile.branch}
              onChange={(e) => updateField("branch", e.target.value)}
            >
              <option value="">Not set — showing electives from all branches</option>
              {BRANCHES.map((b) => (
                <option key={b} value={b}>
                  {b}
                </option>
              ))}
            </select>
          </div>

          <div>
            <p className="label-tag mb-2 text-ink/50">Career Goal</p>
            <ChipSelect
              options={CAREER_GOALS}
              selected={profile.career_goal ? [profile.career_goal] : []}
              onToggle={(goal) =>
                updateField("career_goal", profile.career_goal === goal ? "" : goal)
              }
            />
          </div>

          <div>
            <p className="label-tag mb-2 text-ink/50">Configured Passions</p>
            <ChipSelect
              options={INTEREST_TAGS}
              selected={profile.interests}
              onToggle={(tag) =>
                updateField(
                  "interests",
                  profile.interests.includes(tag)
                    ? profile.interests.filter((t) => t !== tag)
                    : [...profile.interests, tag]
                )
              }
            />
          </div>

          <div className="mt-2 flex items-center gap-4">
            <button type="button" onClick={handleSave} disabled={isSaving} className="btn-primary">
              {isSaving ? "Saving..." : "Save Profile"}
            </button>
            {savedAt && <span className="label-tag text-moss">Saved.</span>}
          </div>
        </div>
      </div>
    </div>
  );
}
