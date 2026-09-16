import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

export const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("moira_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      const messages = detail.map((d) => (typeof d?.msg === "string" ? d.msg : null)).filter(Boolean);
      if (messages.length > 0) return messages.join("; ");
    }
    if (error.message) return error.message;
  }
  return "Something went wrong. Please try again.";
}
