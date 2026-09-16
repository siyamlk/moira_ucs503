import { useEffect, useMemo, useState } from "react";

import { EmptyState } from "../../components/common/EmptyState";
import { ErrorBanner } from "../../components/common/ErrorBanner";
import { LoadingState } from "../../components/common/LoadingState";
import { PlateTag } from "../../components/common/PlateTag";
import { FacultyCard } from "../../components/faculty/FacultyCard";
import { getApiErrorMessage } from "../../services/api";
import { facultyService } from "../../services/facultyService";
import type { Faculty } from "../../types";

const PAGE_SIZE = 12;

export function FacultyPage() {
  const [faculty, setFaculty] = useState<Faculty[]>([]);
  const [query, setQuery] = useState("");
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    facultyService
      .list()
      .then(setFaculty)
      .catch((err) => setError(getApiErrorMessage(err)))
      .finally(() => setIsLoading(false));
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return faculty;
    return faculty.filter((f) =>
      [f.name, f.department, f.specialization, f.title, ...f.research_interests]
        .join(" ")
        .toLowerCase()
        .includes(q)
    );
  }, [faculty, query]);

  const visible = filtered.slice(0, visibleCount);

  return (
    <div className="flex flex-col gap-8">
      <div className="card-plate p-6 sm:p-8">
        <PlateTag>Faculty Corner</PlateTag>
        <h1 className="mt-4 font-serif text-3xl font-bold text-ink sm:text-4xl">
          Knock on the right door.
        </h1>
        <p className="mt-2 max-w-2xl text-ink/70">
          Explore faculty profiles, their areas of expertise, and where to find them.
        </p>

        <input
          className="field-input mt-6"
          placeholder="Search by name, department, or specialization..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setVisibleCount(PAGE_SIZE);
          }}
        />
        <p className="label-tag mt-2 text-ink/40">{filtered.length} faculty found</p>
      </div>

      {error && <ErrorBanner message={error} />}

      {isLoading ? (
        <LoadingState label="Loading faculty directory..." />
      ) : filtered.length === 0 ? (
        <EmptyState title="No faculty match your search" description="Try a different name or specialization." />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {visible.map((f) => (
              <FacultyCard key={f.id} faculty={f} />
            ))}
          </div>
          {visibleCount < filtered.length && (
            <button
              type="button"
              className="btn-outline mx-auto"
              onClick={() => setVisibleCount((c) => c + PAGE_SIZE)}
            >
              Load More
            </button>
          )}
        </>
      )}
    </div>
  );
}
