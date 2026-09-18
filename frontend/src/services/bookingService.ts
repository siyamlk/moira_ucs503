import { api } from "./api";
import type { Booking } from "../types";

export const bookingService = {
  async list(): Promise<Booking[]> {
    const { data } = await api.get<Booking[]>("/bookings");
    return data;
  },

  async book(facultyScheduleId: number): Promise<Booking> {
    const { data } = await api.post<Booking>("/bookings", {
      faculty_schedule_id: facultyScheduleId,
    });
    return data;
  },

  async cancel(bookingId: number): Promise<void> {
    await api.delete(`/bookings/${bookingId}`);
  },
};
