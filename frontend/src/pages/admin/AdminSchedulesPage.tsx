import { useEffect, useState } from "react";

import { AdminTable, type AdminTableColumn } from "../../components/admin/AdminTable";
import { ConfirmDialog } from "../../components/admin/ConfirmDialog";
import { EmptyState } from "../../components/common/EmptyState";
import { ErrorBanner } from "../../components/common/ErrorBanner";
import { LoadingState } from "../../components/common/LoadingState";
import { PlateTag } from "../../components/common/PlateTag";
import { TextField } from "../../components/forms/TextField";
import { getApiErrorMessage } from "../../services/api";
import { adminFacultyService } from "../../services/adminFacultyService";
import { adminScheduleService } from "../../services/adminScheduleService";
import type { AdminFaculty, AdminSchedule, AdminScheduleInput } from "../../types/admin";

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

function emptyForm(facultyId: number | null): AdminScheduleInput {
  return {
    faculty_id: facultyId ?? 0,
    day: "Monday",
    start_time: "10:00",
    end_time: "11:00",
    room: "",
    note: "Office Hours",
    semester: "",
  };
}

export function AdminSchedulesPage() {
  const [faculty, setFaculty] = useState<AdminFaculty[]>([]);
  const [facultyFilter, setFacultyFilter] = useState<number | null>(null);
  const [schedules, setSchedules] = useState<AdminSchedule[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<AdminScheduleInput | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<AdminSchedule | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  async function loadSchedules() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await adminScheduleService.list(facultyFilter ?? undefined);
      setSchedules(data);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    adminFacultyService.list().then(setFaculty).catch(() => setFaculty([]));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    loadSchedules();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [facultyFilter]);

  function startCreate() {
    setEditingId(null);
    setForm(emptyForm(facultyFilter));
    setFormError(null);
  }

  function startEdit(schedule: AdminSchedule) {
    setEditingId(schedule.id);
    setForm({
      faculty_id: schedule.faculty_id,
      day: schedule.day,
      start_time: schedule.start_time,
      end_time: schedule.end_time,
      room: schedule.room,
      note: schedule.note,
      semester: schedule.semester,
    });
    setFormError(null);
  }

  function cancelForm() {
    setForm(null);
    setEditingId(null);
    setFormError(null);
  }

  async function handleSave() {
    if (!form) return;
    setFormError(null);
    setIsSaving(true);
    try {
      if (editingId !== null) {
        await adminScheduleService.update(editingId, form);
      } else {
        await adminScheduleService.create(form);
      }
      cancelForm();
      await loadSchedules();
    } catch (err) {
      setFormError(getApiErrorMessage(err));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    setIsDeleting(true);
    try {
      await adminScheduleService.remove(deleteTarget.id);
      setDeleteTarget(null);
      await loadSchedules();
    } catch (err) {
      setError(getApiErrorMessage(err));
      setDeleteTarget(null);
    } finally {
      setIsDeleting(false);
    }
  }

  function facultyName(id: number): string {
    return faculty.find((f) => f.id === id)?.name ?? `#${id}`;
  }

  const columns: AdminTableColumn<AdminSchedule>[] = [
    { header: "Faculty", render: (s) => facultyName(s.faculty_id) },
    { header: "Day", render: (s) => s.day },
    { header: "Time", render: (s) => `${s.start_time} – ${s.end_time}` },
    { header: "Room", render: (s) => s.room || "—" },
    { header: "Semester", render: (s) => s.semester || "Standing" },
    { header: "Note", render: (s) => s.note },
  ];

  return (
    <div className="flex flex-col gap-8">
      <div className="card-plate p-6 sm:p-8">
        <PlateTag>Admin &middot; Schedules</PlateTag>
        <h1 className="mt-4 font-serif text-3xl font-bold text-ink">Manage faculty office hours</h1>
        <p className="mt-2 max-w-2xl text-ink/70">
          Office hours, room, and semester-specific slots are entered here by admins — nothing is
          inferred automatically.
        </p>

        <div className="mt-6 flex flex-wrap items-end gap-3">
          <div className="min-w-[220px]">
            <label className="label-tag mb-1.5 block text-ink">Filter by faculty</label>
            <select
              className="field-input"
              value={facultyFilter ?? ""}
              onChange={(e) => setFacultyFilter(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">All faculty</option>
              {faculty.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.name}
                </option>
              ))}
            </select>
          </div>
          <button type="button" className="btn-primary" onClick={startCreate} disabled={faculty.length === 0}>
            + Add Schedule Entry
          </button>
        </div>
      </div>

      {error && <ErrorBanner message={error} />}

      {form && (
        <div className="card-plate p-6 sm:p-8">
          <h2 className="font-serif text-xl font-bold text-ink">
            {editingId !== null ? "Edit Schedule Entry" : "Add Schedule Entry"}
          </h2>

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="label-tag mb-1.5 block text-ink">Faculty</label>
              <select
                className="field-input"
                value={form.faculty_id || ""}
                onChange={(e) => setForm({ ...form, faculty_id: Number(e.target.value) })}
              >
                <option value="">— Select faculty —</option>
                {faculty.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="label-tag mb-1.5 block text-ink">Day</label>
              <select
                className="field-input"
                value={form.day}
                onChange={(e) => setForm({ ...form, day: e.target.value })}
              >
                {DAYS.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </div>
            <TextField
              label="Start Time"
              type="time"
              value={form.start_time}
              onChange={(e) => setForm({ ...form, start_time: e.target.value })}
            />
            <TextField
              label="End Time"
              type="time"
              value={form.end_time}
              onChange={(e) => setForm({ ...form, end_time: e.target.value })}
            />
            <TextField
              label="Room"
              value={form.room ?? ""}
              onChange={(e) => setForm({ ...form, room: e.target.value })}
            />
            <TextField
              label="Semester"
              value={form.semester ?? ""}
              onChange={(e) => setForm({ ...form, semester: e.target.value })}
              helpText='e.g. "Odd 2026-27" — leave blank for a standing slot'
            />
            <TextField
              label="Note"
              value={form.note ?? ""}
              onChange={(e) => setForm({ ...form, note: e.target.value })}
            />
          </div>

          {formError && (
            <div className="mt-4">
              <ErrorBanner message={formError} />
            </div>
          )}

          <div className="mt-6 flex gap-3">
            <button
              type="button"
              className="btn-primary"
              onClick={handleSave}
              disabled={isSaving || !form.faculty_id}
            >
              {isSaving ? "Saving..." : "Save"}
            </button>
            <button type="button" className="btn-outline" onClick={cancelForm} disabled={isSaving}>
              Cancel
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <LoadingState label="Loading schedules..." />
      ) : schedules.length === 0 ? (
        <EmptyState
          title="No schedule entries yet"
          description="Add office hours or class slots for a faculty member."
        />
      ) : (
        <AdminTable
          columns={columns}
          rows={schedules}
          getRowKey={(s) => s.id}
          onEdit={startEdit}
          onDelete={setDeleteTarget}
        />
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="Delete this schedule entry?"
          message={`This removes the ${deleteTarget.day} ${deleteTarget.start_time}–${deleteTarget.end_time} slot for ${facultyName(deleteTarget.faculty_id)}.`}
          confirmLabel="Delete"
          isBusy={isDeleting}
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  );
}
