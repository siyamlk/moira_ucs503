import type { Faculty } from "../../types";
import { formatTime } from "../../utils/format";

export function FacultyMiniCard({ faculty }: { faculty: Faculty }) {
  return (
    <div className="border-2 border-ink bg-parchmentDark p-3">
      <p className="font-serif text-sm font-bold text-ink">{faculty.name}</p>
      <p className="text-xs text-ink/60">{faculty.title}</p>
      {faculty.specialization && (
        <p className="mt-1 text-xs text-ink/70">
          <span className="font-semibold">Specialization:</span> {faculty.specialization}
        </p>
      )}
      {faculty.schedules.length > 0 ? (
        <ul className="mt-2 space-y-0.5 text-xs text-ink/70">
          {faculty.schedules.map((s) => (
            <li key={s.id}>
              {s.day} &middot; {formatTime(s.start_time)}&ndash;{formatTime(s.end_time)} &middot; {s.room}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-xs italic text-ink/40">Office hours not yet available.</p>
      )}
    </div>
  );
}
