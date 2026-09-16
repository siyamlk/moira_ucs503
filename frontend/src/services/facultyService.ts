import { api } from "./api";
import type { Faculty } from "../types";

export const facultyService = {
  async list(): Promise<Faculty[]> {
    const { data } = await api.get<Faculty[]>("/faculty");
    return data;
  },

  async get(id: number): Promise<Faculty> {
    const { data } = await api.get<Faculty>(`/faculty/${id}`);
    return data;
  },
};
