import { api } from "./api";
import type { Elective, RecommendRequestPayload, RecommendResponse } from "../types";

export const electiveService = {
  async list(): Promise<Elective[]> {
    const { data } = await api.get<Elective[]>("/electives");
    return data;
  },

  async get(id: number): Promise<Elective> {
    const { data } = await api.get<Elective>(`/electives/${id}`);
    return data;
  },

  async recommend(payload: RecommendRequestPayload): Promise<RecommendResponse> {
    const { data } = await api.post<RecommendResponse>("/electives/recommend", payload);
    return data;
  },
};
