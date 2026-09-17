import { useEffect, useState } from "react";

import { AdminTable, type AdminTableColumn } from "../../components/admin/AdminTable";
import { ConfirmDialog } from "../../components/admin/ConfirmDialog";
import { EmptyState } from "../../components/common/EmptyState";
import { ErrorBanner } from "../../components/common/ErrorBanner";
import { LoadingState } from "../../components/common/LoadingState";
import { PlateTag } from "../../components/common/PlateTag";
import { TagListInput } from "../../components/forms/TagListInput";
import { TextField } from "../../components/forms/TextField";
import { getApiErrorMessage } from "../../services/api";
import { adminFacultyService } from "../../services/adminFacultyService";
import type { AdminFaculty, AdminFacultyInput } from "../../types/admin";

const EMPTY_FORM: AdminFacultyInput = {
  ref_code: "",
  name: "",
  title: "",
  department: "Department of Computer Science",
  specialization: "",
  research_interests: [],
  office_location: "",
  email: "",
  photo_url: "",
  profile_url: "",
};

export function AdminFacultyPage() {
  const [faculty, setFaculty] = useState<AdminFaculty[]>([]);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<AdminFacultyInput | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<AdminFaculty | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  async function loadFaculty() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await adminFacultyService.list(search ? { search } : {});
      setFaculty(data);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadFaculty();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function startCreate() {
    setEditingId(null);
    setForm({ ...EMPTY_FORM });
    setFormError(null);
  }

  function startEdit(member: AdminFaculty) {
    setEditingId(member.id);
    setForm({
      ref_code: member.ref_code,
      name: member.name,
      title: member.title,
      department: member.department,
      specialization: member.specialization,
      research_interests: member.research_interests,
      office_location: member.office_location,
      email: member.email,
      photo_url: member.photo_url,
      profile_url: member.profile_url,
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
        await adminFacultyService.update(editingId, form);
      } else {
        await adminFacultyService.create(form);
      }
      cancelForm();
      await loadFaculty();
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
      await adminFacultyService.remove(deleteTarget.id);
      setDeleteTarget(null);
      await loadFaculty();
    } catch (err) {
      setError(getApiErrorMessage(err));
      setDeleteTarget(null);
    } finally {
      setIsDeleting(false);
    }
  }

  const columns: AdminTableColumn<AdminFaculty>[] = [
    { header: "Ref Code", render: (f) => <span className="font-mono font-bold">{f.ref_code}</span> },
    { header: "Name", render: (f) => f.name },
    { header: "Title", render: (f) => f.title || "—" },
    { header: "Department", render: (f) => f.department || "—" },
    { header: "Email", render: (f) => f.email || "—" },
    { header: "Schedules", render: (f) => f.schedules.length },
  ];

  return (
    <div className="flex flex-col gap-8">
      <div className="card-plate p-6 sm:p-8">
        <PlateTag>Admin &middot; Faculty</PlateTag>
        <h1 className="mt-4 font-serif text-3xl font-bold text-ink">Manage the faculty directory</h1>
        <p className="mt-2 max-w-2xl text-ink/70">
          This directory is what the student-facing Faculty page and faculty-matching in
          recommendations read from directly.
        </p>

        <div className="mt-6 flex flex-wrap items-end gap-3">
          <div className="min-w-[220px] flex-1">
            <TextField
              label="Search"
              placeholder="Search by name or ref code"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && loadFaculty()}
            />
          </div>
          <button type="button" className="btn-outline" onClick={loadFaculty}>
            Search
          </button>
          <button type="button" className="btn-primary" onClick={startCreate}>
            + Add Faculty
          </button>
        </div>
      </div>

      {error && <ErrorBanner message={error} />}

      {form && (
        <div className="card-plate p-6 sm:p-8">
          <h2 className="font-serif text-xl font-bold text-ink">
            {editingId !== null ? "Edit Faculty Member" : "Add Faculty Member"}
          </h2>

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <TextField
              label="Ref Code"
              required
              value={form.ref_code}
              onChange={(e) => setForm({ ...form, ref_code: e.target.value })}
            />
            <TextField
              label="Name"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
            <TextField
              label="Title"
              value={form.title ?? ""}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
            <TextField
              label="Department"
              value={form.department ?? ""}
              onChange={(e) => setForm({ ...form, department: e.target.value })}
            />
            <TextField
              label="Office Location"
              value={form.office_location ?? ""}
              onChange={(e) => setForm({ ...form, office_location: e.target.value })}
            />
            <TextField
              label="Email"
              type="email"
              value={form.email ?? ""}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
            <TextField
              label="Photo URL"
              value={form.photo_url ?? ""}
              onChange={(e) => setForm({ ...form, photo_url: e.target.value })}
            />
            <TextField
              label="Profile URL"
              value={form.profile_url ?? ""}
              onChange={(e) => setForm({ ...form, profile_url: e.target.value })}
            />
          </div>

          <div className="mt-4">
            <label className="label-tag mb-1.5 block text-ink">Specialization</label>
            <textarea
              className="field-input min-h-[70px] resize-y"
              value={form.specialization ?? ""}
              onChange={(e) => setForm({ ...form, specialization: e.target.value })}
            />
          </div>

          <div className="mt-4">
            <TagListInput
              label="Research Interests"
              values={form.research_interests ?? []}
              onChange={(v) => setForm({ ...form, research_interests: v })}
              placeholder="Add a research interest"
            />
          </div>

          {formError && (
            <div className="mt-4">
              <ErrorBanner message={formError} />
            </div>
          )}

          <div className="mt-6 flex gap-3">
            <button type="button" className="btn-primary" onClick={handleSave} disabled={isSaving}>
              {isSaving ? "Saving..." : "Save"}
            </button>
            <button type="button" className="btn-outline" onClick={cancelForm} disabled={isSaving}>
              Cancel
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <LoadingState label="Loading faculty..." />
      ) : faculty.length === 0 ? (
        <EmptyState title="No faculty yet" description="Add your first faculty member to get started." />
      ) : (
        <AdminTable
          columns={columns}
          rows={faculty}
          getRowKey={(f) => f.id}
          onEdit={startEdit}
          onDelete={setDeleteTarget}
        />
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="Delete this faculty member?"
          message={`This permanently removes ${deleteTarget.name} and their schedule entries. If any electives are still assigned to them, this will be blocked until you reassign or clear those first.`}
          confirmLabel="Delete"
          isBusy={isDeleting}
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  );
}
