import { create } from "zustand";
import { api } from "@/lib/api";

type User = { id: string; username: string; email: string; role: "super_admin" | "admin"; barangay_id?: string | null };

type AuthStore = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
};

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  async login(username, password) {
    set({ isLoading: true });
    const res = await api.post("/api/auth/login", { username, password });
    localStorage.setItem("access_token", res.data.access_token);
    localStorage.setItem("refresh_token", res.data.refresh_token);
    set({ user: res.data.user, isAuthenticated: true, isLoading: false });
  },
  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null, isAuthenticated: false });
  },
  async refreshUser() {
    const res = await api.get("/api/auth/me");
    set({ user: res.data, isAuthenticated: true });
  },
}));
