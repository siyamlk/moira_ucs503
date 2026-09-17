import { api } from "./api";
import type { AdminFaculty, AdminFacultyInput } from "../types/admin";

export interface AdminFacultyFilters {
  search?: string;
  department?: string;
}

export const adminFacultyService = {
  async list(filters: AdminFacultyFilters = {}): Promise<AdminFaculty[]> {
    const { data } = await api.get<AdminFaculty[]>("/admin/faculty", { params: filters });
    return data;
  },

  async create(payload: AdminFacultyInput): Promise<AdminFaculty> {
    const { data } = await api.post<AdminFaculty>("/admin/faculty", payload);
    return data;
  },

  async update(id: number, payload: Partial<AdminFacultyInput>): Promise<AdminFaculty> {
    const { data } = await api.put<AdminFaculty>(`/admin/faculty/${id}`, payload);
    return data;
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/admin/faculty/${id}`);
  },
};
