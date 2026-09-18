import type { Faculty } from "../../types";
import { ScheduleSlotRow } from "./ScheduleSlotRow";

export function FacultyCard({ faculty }: { faculty: Faculty }) {
  return (
    <div className="card-plate flex flex-col gap-3 p-5">
      <div className="flex items-start justify-between">
        <span className="label-tag bg-parchmentDark px-2 py-1 text-ink/60">{faculty.department}</span>
        <span className="label-tag text-ink/40">REF #{faculty.ref_code}</span>
      </div>

      <div className="flex items-center gap-3">
        {faculty.photo_url ? (
          <img
            src={faculty.photo_url}
            alt={faculty.name}
            className="h-12 w-12 border-2 border-ink object-cover"
            loading="lazy"
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).style.display = "none";
            }}
          />
        ) : (
          <div className="flex h-12 w-12 items-center justify-center border-2 border-ink bg-mossLight font-mono text-sm font-bold text-ink">
            {faculty.name.slice(0, 2).toUpperCase()}
          </div>
        )}
        <div>
          <p className="font-serif text-lg font-bold leading-tight text-ink">{faculty.name}</p>
          <p className="text-sm text-ink/60">{faculty.title}</p>
        </div>
      </div>

      {faculty.specialization && (
        <div>
          <p className="label-tag text-ink/50">Specialization</p>
          <p className="text-sm text-ink">{faculty.specialization}</p>
        </div>
      )}

      <div>
        <p className="label-tag text-ink/50">Office Hours</p>
        {faculty.schedules.length > 0 ? (
          <ul className="mt-1 space-y-1 text-sm text-ink/70">
            {faculty.schedules.map((s) => (
              <ScheduleSlotRow key={s.id} schedule={s} />
            ))}
          </ul>
        ) : (
          <p className="text-sm italic text-ink/40">Not yet available.</p>
        )}
      </div>

      <div className="mt-auto flex items-center justify-between border-t-2 border-ink pt-3 text-xs">
        {faculty.email ? (
          <a href={`mailto:${faculty.email}`} className="label-tag text-moss hover:underline">
            {faculty.email}
          </a>
        ) : (
          <span />
        )}
        {faculty.profile_url && (
          <a
            href={faculty.profile_url}
            target="_blank"
            rel="noreferrer"
            className="label-tag text-ink hover:underline"
          >
            Full Profile →
          </a>
        )}
      </div>
    </div>
  );
}
