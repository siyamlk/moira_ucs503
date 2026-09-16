import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { LoadingState } from "../../components/common/LoadingState";
import { PlateTag } from "../../components/common/PlateTag";
import { useAuth } from "../../context/AuthContext";
import { backlogService } from "../../services/backlogService";
import { profileService } from "../../services/profileService";
import type { Backlog, Profile } from "../../types";

export function DashboardPage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [backlogs, setBacklogs] = useState<Backlog[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    Promise.all([profileService.get(), backlogService.list()])
      .then(([p, b]) => {
        setProfile(p);
        setBacklogs(b);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const pendingBacklogs = backlogs.filter((b) => b.status === "pending");

  return (
    <div className="flex flex-col gap-8">
      <div className="card-plate p-6 sm:p-8">
        <PlateTag>Your Academic Map</PlateTag>
        <h1 className="mt-4 font-serif text-3xl font-bold text-ink sm:text-4xl">
          Every choice draws a path.
          <br />
          <span className="italic text-ink/70">Find your way forward.</span>
        </h1>
        <p className="mt-3 max-w-2xl text-ink/70">
          Your university journey isn&apos;t a straight line. It&apos;s an evolving territory of
          electives, academic decisions, pending courses, and people who can help you find your
          way — welcome back, {user?.full_name.split(" ")[0]}.
        </p>
      </div>

      {isLoading ? (
        <LoadingState label="Loading your map..." />
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <Link to="/recommendations" className="card-plate flex flex-col gap-3 p-6 transition-transform hover:-translate-y-1">
            <span className="label-tag bg-parchmentDark px-2 py-1 text-ink/60">Elective Advisor</span>
            <p className="font-serif text-xl font-bold text-ink">Find electives that fit you.</p>
            <p className="text-sm text-ink/60">
              Focus area:{" "}
              {profile?.interests.length ? profile.interests.slice(0, 2).join(", ") : "Not set yet"}
            </p>
            <span className="btn-outline mt-auto">Explore →</span>
          </Link>

          <Link to="/backlogs" className="card-plate flex flex-col gap-3 p-6 transition-transform hover:-translate-y-1">
            <span className="label-tag bg-rose/50 px-2 py-1 text-ink">Backlog Advisor</span>
            <p className="font-serif text-xl font-bold text-ink">Prioritize your backlogs.</p>
            <p className="text-sm text-ink/60">
              {pendingBacklogs.length > 0
                ? `${pendingBacklogs.length} course${pendingBacklogs.length === 1 ? "" : "s"} need action`
                : "No pending backlogs"}
            </p>
            <span className="btn-outline mt-auto">View Backlogs →</span>
          </Link>

          <Link to="/profile" className="card-plate flex flex-col gap-3 p-6 transition-transform hover:-translate-y-1">
            <span className="label-tag bg-mossLight px-2 py-1 text-ink/60">My Moira</span>
            <p className="font-serif text-xl font-bold text-ink">Your open notebook.</p>
            <p className="text-sm text-ink/60">
              CGPA {profile?.cgpa.toFixed(2) ?? "--"} &middot; Sem {profile?.semester ?? "--"}
            </p>
            <span className="btn-outline mt-auto">Open Profile →</span>
          </Link>
        </div>
      )}

      <div className="sticky-note w-fit">&ldquo;Your future isn&apos;t something you have to figure out alone.&rdquo;</div>
    </div>
  );
}
