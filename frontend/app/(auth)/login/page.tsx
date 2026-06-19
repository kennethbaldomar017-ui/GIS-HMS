"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldCheck } from "lucide-react";
import { useAuthStore } from "@/store/auth";

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const [username, setUsername] = useState("superadmin");
  const [password, setPassword] = useState("Admin@123");
  const [error, setError] = useState("");

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await login(username, password);
      router.push("/dashboard");
    } catch {
      setError("Invalid username or password.");
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-slate-100 p-4">
      <form onSubmit={submit} className="w-full max-w-sm rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-6 flex items-center gap-3">
          <ShieldCheck className="h-8 w-8 text-brand" />
          <div>
            <h1 className="text-xl font-semibold">GIS-HMS</h1>
            <p className="text-sm text-muted">Cabadbaran child nutrition monitoring</p>
          </div>
        </div>
        <label className="mb-3 block text-sm font-medium">Username<input className="mt-1 w-full rounded border border-slate-300 px-3 py-2" value={username} onChange={(e) => setUsername(e.target.value)} /></label>
        <label className="mb-4 block text-sm font-medium">Password<input type="password" className="mt-1 w-full rounded border border-slate-300 px-3 py-2" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        {error && <p className="mb-3 rounded bg-red-50 p-2 text-sm text-red-700">{error}</p>}
        <button className="w-full rounded bg-brand px-4 py-2 font-semibold text-white">Sign in</button>
      </form>
    </main>
  );
}
