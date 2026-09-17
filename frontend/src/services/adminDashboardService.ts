import { api } from "./api";
import type { DashboardStats } from "../types/admin";

export const adminDashboardService = {
  async get(): Promise<DashboardStats> {
    const { data } = await api.get<DashboardStats>("/admin/dashboard");
    return data;
  },
};
