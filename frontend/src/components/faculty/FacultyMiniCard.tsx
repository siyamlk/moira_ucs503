import type { Faculty } from "../../types";
import { ScheduleSlotRow } from "./ScheduleSlotRow";

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
        <ul className="mt-2 space-y-1 text-xs text-ink/70">
          {faculty.schedules.map((s) => (
            <ScheduleSlotRow key={s.id} schedule={s} />
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-xs italic text-ink/40">Office hours not yet available.</p>
      )}
    </div>
  );
}
