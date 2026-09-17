import { api } from "./api";
import type { AdminElective, AdminElectiveInput } from "../types/admin";

export interface AdminElectiveFilters {
  search?: string;
  department?: string;
  category?: string;
  basket?: string;
}

export const adminElectiveService = {
  async list(filters: AdminElectiveFilters = {}): Promise<AdminElective[]> {
    const { data } = await api.get<AdminElective[]>("/admin/electives", { params: filters });
    return data;
  },

  async create(payload: AdminElectiveInput): Promise<AdminElective> {
    const { data } = await api.post<AdminElective>("/admin/electives", payload);
    return data;
  },

  async update(id: number, payload: Partial<AdminElectiveInput>): Promise<AdminElective> {
    const { data } = await api.put<AdminElective>(`/admin/electives/${id}`, payload);
    return data;
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/admin/electives/${id}`);
  },
};
