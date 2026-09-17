import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ErrorBanner } from "../../components/common/ErrorBanner";
import { LoadingState } from "../../components/common/LoadingState";
import { PlateTag } from "../../components/common/PlateTag";
import { adminDashboardService } from "../../services/adminDashboardService";
import { getApiErrorMessage } from "../../services/api";
import type { DashboardStats } from "../../types/admin";

function StatTile({ label, value }: { label: string; value: number }) {
  return (
    <div className="card-plate p-5">
      <p className="label-tag text-ink/50">{label}</p>
      <p className="mt-2 font-serif text-4xl font-bold text-ink">{value}</p>
    </div>
  );
}

function describeAction(action: string, entityType: string): string {
  return `${action} ${entityType.replace("_", " ")}`;
}

export function AdminDashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    adminDashboardService
      .get()
      .then(setStats)
      .catch((err) => setError(getApiErrorMessage(err)))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="flex flex-col gap-8">
      <div className="card-plate p-6 sm:p-8">
        <PlateTag>Admin &middot; Dashboard</PlateTag>
        <h1 className="mt-4 font-serif text-3xl font-bold text-ink">Academic data console</h1>
        <p className="mt-2 max-w-2xl text-ink/70">
          A snapshot of the data the advisory engines run on, and the most recent changes admins
          have made.
        </p>
      </div>

      {error && <ErrorBanner message={error} />}

      {isLoading ? (
        <LoadingState label="Loading dashboard..." />
      ) : stats ? (
        <>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <StatTile label="Electives" value={stats.total_electives} />
            <StatTile label="Faculty" value={stats.total_faculty} />
            <StatTile label="EFB Baskets" value={stats.total_baskets} />
            <StatTile label="Categories" value={stats.total_categories} />
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Link to="/admin/electives" className="btn-outline justify-center">
              Manage Electives
            </Link>
            <Link to="/admin/faculty" className="btn-outline justify-center">
              Manage Faculty
            </Link>
            <Link to="/admin/schedules" className="btn-outline justify-center">
              Manage Schedules
            </Link>
            <Link to="/admin/config" className="btn-outline justify-center">
              Manage Rules
            </Link>
          </div>

          <div className="card-plate p-6">
            <p className="label-tag mb-3 text-ink/50">Recently updated records</p>
            {stats.recent_activity.length === 0 ? (
              <p className="text-sm text-ink/60">No admin actions recorded yet.</p>
            ) : (
              <ul className="flex flex-col divide-y divide-ink/10">
                {stats.recent_activity.map((entry) => (
                  <li key={entry.id} className="flex items-center justify-between gap-4 py-2 text-sm">
                    <span className="text-ink/80">
                      {describeAction(entry.action, entry.entity_type)}
                      {entry.entity_id !== null && <span className="text-ink/50"> #{entry.entity_id}</span>}
                    </span>
                    <span className="label-tag text-ink/40">{new Date(entry.created_at).toLocaleString()}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      ) : null}
    </div>
  );
}
