import { api } from "./api";
import type { AcademicConfig, AcademicConfigUpdatePayload } from "../types/admin";

export const adminConfigService = {
  async list(): Promise<AcademicConfig[]> {
    const { data } = await api.get<AcademicConfig[]>("/admin/config");
    return data;
  },

  async get(key: string): Promise<AcademicConfig> {
    const { data } = await api.get<AcademicConfig>(`/admin/config/${key}`);
    return data;
  },

  async update(key: string, payload: AcademicConfigUpdatePayload): Promise<AcademicConfig> {
    const { data } = await api.put<AcademicConfig>(`/admin/config/${key}`, payload);
    return data;
  },
};
