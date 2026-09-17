import { api } from "./api";
import type { AdminSchedule, AdminScheduleInput } from "../types/admin";

export const adminScheduleService = {
  async list(facultyId?: number): Promise<AdminSchedule[]> {
    const { data } = await api.get<AdminSchedule[]>("/admin/schedules", {
      params: facultyId ? { faculty_id: facultyId } : undefined,
    });
    return data;
  },

  async create(payload: AdminScheduleInput): Promise<AdminSchedule> {
    const { data } = await api.post<AdminSchedule>("/admin/schedules", payload);
    return data;
  },

  async update(id: number, payload: Partial<AdminScheduleInput>): Promise<AdminSchedule> {
    const { data } = await api.put<AdminSchedule>(`/admin/schedules/${id}`, payload);
    return data;
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/admin/schedules/${id}`);
  },
};
