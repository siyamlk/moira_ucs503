import { api } from "./api";
import type { Backlog, BacklogCreatePayload, PrioritizeResponse } from "../types";

export const backlogService = {
  async list(): Promise<Backlog[]> {
    const { data } = await api.get<Backlog[]>("/backlogs");
    return data;
  },

  async create(payload: BacklogCreatePayload): Promise<Backlog> {
    const { data } = await api.post<Backlog>("/backlogs", payload);
    return data;
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/backlogs/${id}`);
  },

  async prioritize(): Promise<PrioritizeResponse> {
    const { data } = await api.post<PrioritizeResponse>("/backlogs/prioritize");
    return data;
  },
};
