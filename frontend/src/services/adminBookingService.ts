import { api } from "./api";
import type { AdminBooking } from "../types/admin";

export const adminBookingService = {
  async list(facultyId?: number): Promise<AdminBooking[]> {
    const { data } = await api.get<AdminBooking[]>("/admin/bookings", {
      params: facultyId ? { faculty_id: facultyId } : undefined,
    });
    return data;
  },

  async cancel(id: number): Promise<void> {
    await api.delete(`/admin/bookings/${id}`);
  },
};
