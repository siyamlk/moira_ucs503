import { api } from "./api";
import type { Profile, ProfileUpdatePayload } from "../types";

export const profileService = {
  async get(): Promise<Profile> {
    const { data } = await api.get<Profile>("/profile");
    return data;
  },

  async update(payload: ProfileUpdatePayload): Promise<Profile> {
    const { data } = await api.put<Profile>("/profile", payload);
    return data;
  },
};
