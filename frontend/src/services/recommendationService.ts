import { api } from "./api";
import type { RecommendationApiResponse, RecommendationRequestPayload } from "../types/recommendation";

export const recommendationService = {
  async recommend(payload: RecommendationRequestPayload): Promise<RecommendationApiResponse> {
    const { data } = await api.post<RecommendationApiResponse>("/recommendations", payload);
    return data;
  },
};
