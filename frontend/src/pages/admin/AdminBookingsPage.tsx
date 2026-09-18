import { useEffect, useState } from "react";

import { AdminTable, type AdminTableColumn } from "../../components/admin/AdminTable";
import { ConfirmDialog } from "../../components/admin/ConfirmDialog";
import { EmptyState } from "../../components/common/EmptyState";
import { ErrorBanner } from "../../components/common/ErrorBanner";
import { LoadingState } from "../../components/common/LoadingState";
import { PlateTag } from "../../components/common/PlateTag";
import { getApiErrorMessage } from "../../services/api";
import { adminBookingService } from "../../services/adminBookingService";
import type { AdminBooking } from "../../types/admin";
import { formatDate, formatTime } from "../../utils/format";

export function AdminBookingsPage() {
  const [bookings, setBookings] = useState<AdminBooking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancelTarget, setCancelTarget] = useState<AdminBooking | null>(null);
  const [isCancelling, setIsCancelling] = useState(false);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      setBookings(await adminBookingService.list());
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCancel() {
    if (!cancelTarget) return;
    setIsCancelling(true);
    try {
      await adminBookingService.cancel(cancelTarget.id);
      setCancelTarget(null);
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err));
      setCancelTarget(null);
    } finally {
      setIsCancelling(false);
    }
  }

  const active = bookings.filter((b) => b.status === "booked");
  const cancelled = bookings.filter((b) => b.status !== "booked");

  const columns: AdminTableColumn<AdminBooking>[] = [
    { header: "Student", render: (b) => `${b.student_name} (${b.student_email})` },
    { header: "Faculty", render: (b) => b.faculty_name },
    {
      header: "Slot",
      render: (b) =>
        `${b.schedule.day} · ${formatTime(b.schedule.start_time)}–${formatTime(b.schedule.end_time)}${
          b.schedule.room ? ` · ${b.schedule.room}` : ""
        }`,
    },
    { header: "Booked", render: (b) => formatDate(b.created_at) },
  ];

  return (
    <div className="flex flex-col gap-8">
      <div className="card-plate p-6 sm:p-8">
        <PlateTag>Admin &middot; Bookings</PlateTag>
        <h1 className="mt-4 font-serif text-3xl font-bold text-ink">Faculty slot bookings</h1>
        <p className="mt-2 max-w-2xl text-ink/70">
          Every student reservation against a real, admin-entered office-hour slot. Cancelling here
          frees the slot immediately — useful if a professor cancels their office hours.
        </p>
        <p className="label-tag mt-4 text-ink/40">
          {active.length} active &middot; {cancelled.length} cancelled
        </p>
      </div>

      {error && <ErrorBanner message={error} />}

      {isLoading ? (
        <LoadingState label="Loading bookings..." />
      ) : bookings.length === 0 ? (
        <EmptyState
          title="No bookings yet"
          description="Once a student books a faculty office-hour slot, it will show up here."
        />
      ) : (
        <>
          <AdminTable
            columns={columns}
            rows={active}
            getRowKey={(b) => b.id}
            onDelete={setCancelTarget}
          />
          {cancelled.length > 0 && (
            <div className="card-plate p-6 opacity-70">
              <p className="label-tag mb-3 text-ink/50">Cancelled history</p>
              <AdminTable columns={columns} rows={cancelled} getRowKey={(b) => b.id} />
            </div>
          )}
        </>
      )}

      {cancelTarget && (
        <ConfirmDialog
          title="Cancel this booking?"
          message={`This frees ${cancelTarget.faculty_name}'s ${cancelTarget.schedule.day} slot for someone else to book. ${cancelTarget.student_name} will need to book again if they still want it.`}
          confirmLabel="Cancel Booking"
          isBusy={isCancelling}
          onConfirm={handleCancel}
          onCancel={() => setCancelTarget(null)}
        />
      )}
    </div>
  );
}
