import { api } from "./api";
import type { AuthResponse, User } from "../types";

export interface SignupPayload {
  full_name: string;
  student_id: string;
  email: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export const authService = {
  async signup(payload: SignupPayload): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>("/auth/signup", payload);
    return data;
  },

  async login(payload: LoginPayload): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>("/auth/login", payload);
    return data;
  },

  async me(): Promise<User> {
    const { data } = await api.get<User>("/auth/me");
    return data;
  },
};
