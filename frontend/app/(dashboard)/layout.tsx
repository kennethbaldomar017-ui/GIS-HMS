"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { Activity, Bell, Building2, ChartLine, ClipboardList, FileText, Flame, LayoutDashboard, LogOut, Map, Users } from "lucide-react";
import { useAuthStore } from "@/store/auth";

const nav = [
  ["Dashboard", "/dashboard", LayoutDashboard],
  ["Map", "/map", Map],
  ["Heatmap", "/heatmap", Flame],
  ["Children", "/children", Users],
  ["Growth", "/growth", ChartLine],
  ["Reports", "/reports", FileText],
  ["Referrals", "/referrals", ClipboardList],
  ["Alerts", "/alerts", Bell],
];
const adminNav = [["Barangays", "/admin/barangays", Building2], ["Users", "/admin/users", Users], ["Logs", "/admin/logs", Activity]];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, refreshUser, logout } = useAuthStore();

  useEffect(() => {
    if (!localStorage.getItem("access_token")) router.push("/login");
    else refreshUser().catch(() => router.push("/login"));
  }, [refreshUser, router]);

  const items = user?.role === "super_admin" ? [...nav, ...adminNav] : nav;

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 shrink-0 border-r border-slate-200 bg-white p-4">
        <div className="mb-6">
          <p className="text-lg font-bold text-brand">GIS-HMS</p>
          <p className="text-xs text-muted">{user?.role === "super_admin" ? "City Health Office" : "Barangay Health Worker"}</p>
        </div>
        <nav className="space-y-1">
          {items.map(([label, href, Icon]) => (
            <Link key={href as string} href={href as string} className={`flex items-center gap-3 rounded px-3 py-2 text-sm font-medium ${pathname === href ? "bg-teal-50 text-brand" : "text-slate-700 hover:bg-slate-100"}`}>
              <Icon className="h-4 w-4" />{label as string}
            </Link>
          ))}
        </nav>
      </aside>
      <div className="min-w-0 flex-1">
        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6">
          <div><p className="font-semibold">{user?.username || "Loading"}</p><p className="text-xs text-muted">{user?.email}</p></div>
          <button onClick={() => { logout(); router.push("/login"); }} className="inline-flex items-center gap-2 rounded border border-slate-300 px-3 py-2 text-sm"><LogOut className="h-4 w-4" />Logout</button>
        </header>
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
