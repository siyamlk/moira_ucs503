import { useEffect, useState } from "react";

import { PrioritizedBacklogRow } from "../../components/backlogs/PrioritizedBacklogRow";
import { BacklogForm } from "../../components/backlogs/BacklogForm";
import { EmptyState } from "../../components/common/EmptyState";
import { ErrorBanner } from "../../components/common/ErrorBanner";
import { LoadingState } from "../../components/common/LoadingState";
import { PlateTag } from "../../components/common/PlateTag";
import { backlogService } from "../../services/backlogService";
import { getApiErrorMessage } from "../../services/api";
import type { Backlog, BacklogCreatePayload, PrioritizeResponse } from "../../types";

export function BacklogsPage() {
  const [backlogs, setBacklogs] = useState<Backlog[]>([]);
  const [prioritized, setPrioritized] = useState<PrioritizeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPrioritizing, setIsPrioritizing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadBacklogs() {
    setIsLoading(true);
    try {
      const data = await backlogService.list();
      setBacklogs(data);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadBacklogs();
  }, []);

  async function handleAdd(payload: BacklogCreatePayload) {
    setError(null);
    try {
      await backlogService.create(payload);
      await loadBacklogs();
      setPrioritized(null);
    } catch (err) {
      setError(getApiErrorMessage(err));
    }
  }

  async function handleRemove(id: number) {
    try {
      await backlogService.remove(id);
      await loadBacklogs();
      setPrioritized(null);
    } catch (err) {
      setError(getApiErrorMessage(err));
    }
  }

  async function handlePrioritize() {
    setError(null);
    setIsPrioritizing(true);
    try {
      const result = await backlogService.prioritize();
      setPrioritized(result);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsPrioritizing(false);
    }
  }

  return (
    <div className="flex flex-col gap-8">
      <div className="card-plate p-6 sm:p-8">
        <PlateTag>Backlog Advisor</PlateTag>
        <h1 className="mt-4 font-serif text-3xl font-bold text-ink sm:text-4xl">Unfinished Business.</h1>
        <p className="mt-2 max-w-2xl text-ink/70">
          Prioritize your pending courses based on credit weight and estimated CGPA impact.
        </p>
      </div>

      {error && <ErrorBanner message={error} />}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <p className="label-tag text-ink/50">
              Your Pending Backlogs &middot; {backlogs.length} remaining to clear
            </p>
          </div>

          {isLoading ? (
            <LoadingState label="Loading backlogs..." />
          ) : backlogs.length === 0 ? (
            <EmptyState
              title="No pending backlogs"
              description="Add a course below to start tracking it, or enjoy the clean slate."
            />
          ) : prioritized ? (
            <div className="flex flex-col gap-3">
              {prioritized.prioritized.map((item) => (
                <PrioritizedBacklogRow key={item.backlog.id} item={item} />
              ))}
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {backlogs.map((b) => (
                <div key={b.id} className="flex items-center justify-between border-2 border-ink bg-white p-4">
                  <div>
                    <p className="font-serif text-lg font-bold text-ink">{b.subject}</p>
                    <p className="label-tag text-ink/50">
                      {b.course_code} &middot; {b.credits.toFixed(1)} Credits &middot; Last grade: {b.current_grade}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemove(b.id)}
                    className="label-tag text-clay hover:underline"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex flex-col gap-4">
          <div className="card-plate p-5">
            <p className="label-tag mb-2 text-ink/50">Prioritize Your Backlogs</p>
            <p className="mb-4 text-sm text-ink/70">
              MOIRA will help you identify which pending courses deserve attention first, based on
              credit weight and estimated CGPA impact.
            </p>
            <button
              type="button"
              onClick={handlePrioritize}
              disabled={isPrioritizing || backlogs.length === 0}
              className="btn-primary w-full"
            >
              {isPrioritizing ? "Calculating..." : "Prioritize My Backlogs →"}
            </button>
            {prioritized && (
              <p className="mt-3 text-xs text-ink/50">
                Current CGPA: {prioritized.current_cgpa.toFixed(2)} &middot; {prioritized.pending_count} pending
              </p>
            )}
          </div>

          <div className="sticky-note">&ldquo;Start with one course at a time.&rdquo;</div>

          <BacklogForm onSubmit={handleAdd} />
        </div>
      </div>
    </div>
  );
}
