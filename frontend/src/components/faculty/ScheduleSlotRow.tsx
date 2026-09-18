import { useEffect, useState } from "react";

import { getApiErrorMessage } from "../../services/api";
import { bookingService } from "../../services/bookingService";
import type { FacultySchedule } from "../../types";
import { formatTime } from "../../utils/format";

export function ScheduleSlotRow({ schedule }: { schedule: FacultySchedule }) {
  const [isBooked, setIsBooked] = useState(schedule.is_booked);
  const [myBookingId, setMyBookingId] = useState<number | null>(null);
  const [isWorking, setIsWorking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // A slot can be booked by someone else — check whether it's *mine* so
    // the row can offer "Cancel" instead of a permanently disabled label.
    if (!schedule.is_booked) return;
    bookingService
      .list()
      .then((bookings) => {
        const mine = bookings.find((b) => b.faculty_schedule_id === schedule.id);
        if (mine) setMyBookingId(mine.id);
      })
      .catch(() => {
        // Booking ownership is a nice-to-have here; a failed lookup just
        // leaves the slot shown as booked-by-someone, not an error state.
      });
  }, [schedule.id, schedule.is_booked]);

  async function handleBook() {
    setIsWorking(true);
    setError(null);
    try {
      const booking = await bookingService.book(schedule.id);
      setIsBooked(true);
      setMyBookingId(booking.id);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsWorking(false);
    }
  }

  async function handleCancel() {
    if (!myBookingId) return;
    setIsWorking(true);
    setError(null);
    try {
      await bookingService.cancel(myBookingId);
      setIsBooked(false);
      setMyBookingId(null);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsWorking(false);
    }
  }

  return (
    <li className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1">
      <span>
        {schedule.day} &middot; {formatTime(schedule.start_time)}&ndash;{formatTime(schedule.end_time)}
        {schedule.room && <> &middot; {schedule.room}</>}
      </span>
      {myBookingId ? (
        <button
          type="button"
          onClick={handleCancel}
          disabled={isWorking}
          className="label-tag text-clay hover:underline disabled:opacity-50"
        >
          {isWorking ? "..." : "Cancel Booking"}
        </button>
      ) : isBooked ? (
        <span className="label-tag text-ink/40">Booked</span>
      ) : (
        <button
          type="button"
          onClick={handleBook}
          disabled={isWorking}
          className="label-tag text-moss hover:underline disabled:opacity-50"
        >
          {isWorking ? "..." : "Book Slot"}
        </button>
      )}
      {error && <span className="w-full text-xs text-clay">{error}</span>}
    </li>
  );
}
