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
import { adminConfigService } from "../../services/adminConfigService";
import { adminElectiveService } from "../../services/adminElectiveService";
import { adminFacultyService } from "../../services/adminFacultyService";
import type { AdminElective, AdminElectiveInput, AdminFaculty } from "../../types/admin";

const DEFAULT_CATEGORIES = [
  "Elective I",
  "Elective II",
  "Elective III",
  "Elective IV",
  "Generic Elective",
  "Professional Elective",
];

const EMPTY_FORM: AdminElectiveInput = {
  code: "",
  title: "",
  department: "",
  credits: 4,
  category: "",
  basket: "",
  prerequisites: "",
  description: "",
  topics: [],
  syllabus_outline: [],
  interest_tags: [],
  career_tags: [],
  faculty_id: null,
};

export function AdminElectivesPage() {
  const [electives, setElectives] = useState<AdminElective[]>([]);
  const [faculty, setFaculty] = useState<AdminFaculty[]>([]);
  const [categories, setCategories] = useState<string[]>(DEFAULT_CATEGORIES);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<AdminElectiveInput | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<AdminElective | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  async function loadElectives() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await adminElectiveService.list(search ? { search } : {});
      setElectives(data);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadElectives();
    adminFacultyService
      .list()
      .then(setFaculty)
      .catch(() => {
        /* the faculty picker just stays empty — not fatal for this page */
      });
    adminConfigService
      .get("elective_categories")
      .then((config) => {
        if (Array.isArray(config.value)) setCategories(config.value as string[]);
      })
      .catch(() => {
        /* config not seeded yet — DEFAULT_CATEGORIES already covers this */
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function startCreate() {
    setEditingId(null);
    setForm({ ...EMPTY_FORM });
    setFormError(null);
  }

  function startEdit(elective: AdminElective) {
    setEditingId(elective.id);
    setForm({
      code: elective.code,
      title: elective.title,
      department: elective.department,
      credits: elective.credits,
      category: elective.category,
      basket: elective.basket,
      prerequisites: elective.prerequisites,
      description: elective.description,
      topics: elective.topics,
      syllabus_outline: elective.syllabus_outline,
      interest_tags: elective.interest_tags,
      career_tags: elective.career_tags,
      faculty_id: elective.faculty_id,
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
        await adminElectiveService.update(editingId, form);
      } else {
        await adminElectiveService.create(form);
      }
      cancelForm();
      await loadElectives();
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
      await adminElectiveService.remove(deleteTarget.id);
      setDeleteTarget(null);
      await loadElectives();
    } catch (err) {
      setError(getApiErrorMessage(err));
      setDeleteTarget(null);
    } finally {
      setIsDeleting(false);
    }
  }

  const columns: AdminTableColumn<AdminElective>[] = [
    { header: "Code", render: (e) => <span className="font-mono font-bold">{e.code}</span> },
    { header: "Title", render: (e) => e.title },
    { header: "Department", render: (e) => e.department || "—" },
    { header: "Category", render: (e) => e.category || "—" },
    { header: "Basket", render: (e) => e.basket || "—" },
    { header: "Credits", render: (e) => e.credits.toFixed(1) },
    {
      header: "Faculty",
      render: (e) => faculty.find((f) => f.id === e.faculty_id)?.name ?? (e.faculty_id ? `#${e.faculty_id}` : "—"),
    },
  ];

  return (
    <div className="flex flex-col gap-8">
      <div className="card-plate p-6 sm:p-8">
        <PlateTag>Admin &middot; Courses &amp; Electives</PlateTag>
        <h1 className="mt-4 font-serif text-3xl font-bold text-ink">Manage the elective catalogue</h1>
        <p className="mt-2 max-w-2xl text-ink/70">
          This is the same catalogue the Elective Advisor, recommendations engine, and Faculty pages
          read from directly — changes here take effect for students immediately.
        </p>

        <div className="mt-6 flex flex-wrap items-end gap-3">
          <div className="min-w-[220px] flex-1">
            <TextField
              label="Search"
              placeholder="Search by code or title"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && loadElectives()}
            />
          </div>
          <button type="button" className="btn-outline" onClick={loadElectives}>
            Search
          </button>
          <button type="button" className="btn-primary" onClick={startCreate}>
            + Add Elective
          </button>
        </div>
      </div>

      {error && <ErrorBanner message={error} />}

      {form && (
        <div className="card-plate p-6 sm:p-8">
          <h2 className="font-serif text-xl font-bold text-ink">
            {editingId !== null ? "Edit Elective" : "Add Elective"}
          </h2>

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <TextField
              label="Code"
              required
              value={form.code}
              onChange={(e) => setForm({ ...form, code: e.target.value })}
            />
            <TextField
              label="Title"
              required
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
            <TextField
              label="Department"
              value={form.department ?? ""}
              onChange={(e) => setForm({ ...form, department: e.target.value })}
            />
            <TextField
              label="Credits"
              type="number"
              step="0.5"
              value={form.credits ?? 4}
              onChange={(e) => setForm({ ...form, credits: Number(e.target.value) })}
            />
            <div>
              <label className="label-tag mb-1.5 block text-ink">Category</label>
              <select
                className="field-input"
                value={form.category ?? ""}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
              >
                <option value="">— None —</option>
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
            <TextField
              label="Basket"
              value={form.basket ?? ""}
              onChange={(e) => setForm({ ...form, basket: e.target.value })}
              helpText="EFB track name, e.g. Data Science"
            />
            <TextField
              label="Prerequisites"
              value={form.prerequisites ?? ""}
              onChange={(e) => setForm({ ...form, prerequisites: e.target.value })}
              helpText="Semicolon-separated, e.g. Data Structures; Operating Systems"
            />
            <div>
              <label className="label-tag mb-1.5 block text-ink">Faculty</label>
              <select
                className="field-input"
                value={form.faculty_id ?? ""}
                onChange={(e) =>
                  setForm({ ...form, faculty_id: e.target.value ? Number(e.target.value) : null })
                }
              >
                <option value="">— Unassigned —</option>
                {faculty.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-4">
            <label className="label-tag mb-1.5 block text-ink">Description</label>
            <textarea
              className="field-input min-h-[90px] resize-y"
              value={form.description ?? ""}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <TagListInput
              label="Topics"
              values={form.topics ?? []}
              onChange={(v) => setForm({ ...form, topics: v })}
              placeholder="Add a topic and press Enter"
            />
            <TagListInput
              label="Interest Tags"
              values={form.interest_tags ?? []}
              onChange={(v) => setForm({ ...form, interest_tags: v })}
              placeholder="Add an interest tag"
              helpText="Drives the recommendation engine's Interest Alignment score"
            />
            <TagListInput
              label="Career Tags"
              values={form.career_tags ?? []}
              onChange={(v) => setForm({ ...form, career_tags: v })}
              placeholder="Add a career tag"
            />
            <TagListInput
              label="Syllabus Outline"
              values={form.syllabus_outline ?? []}
              onChange={(v) => setForm({ ...form, syllabus_outline: v })}
              placeholder="Add a real unit/module heading"
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
        <LoadingState label="Loading electives..." />
      ) : electives.length === 0 ? (
        <EmptyState title="No electives yet" description="Add your first elective to get started." />
      ) : (
        <AdminTable
          columns={columns}
          rows={electives}
          getRowKey={(e) => e.id}
          onEdit={startEdit}
          onDelete={setDeleteTarget}
        />
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="Delete this elective?"
          message={`This permanently removes ${deleteTarget.code} — ${deleteTarget.title}. Students will no longer see it in recommendations.`}
          confirmLabel="Delete"
          isBusy={isDeleting}
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  );
}
