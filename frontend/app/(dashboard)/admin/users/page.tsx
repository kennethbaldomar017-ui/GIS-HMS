"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Panel } from "@/components/ui/Panel";
import { Badge } from "@/components/ui/Badge";

export default function UsersPage() {
  const q = useQuery({ queryKey: ["users"], queryFn: () => api.get("/api/users").then((r) => r.data) });
  return <div className="space-y-6"><h1 className="text-2xl font-semibold">User Management</h1><Panel title="Users"><table className="w-full text-left text-sm"><thead><tr className="border-b"><th className="py-2">Username</th><th>Email</th><th>Role</th><th>Status</th></tr></thead><tbody>{q.data?.map((u: any) => <tr key={u.id} className="border-b last:border-0"><td className="py-2 font-medium">{u.username}</td><td>{u.email}</td><td>{u.role}</td><td><Badge tone={u.is_active ? "normal" : "critical"}>{u.is_active ? "active" : "inactive"}</Badge></td></tr>)}</tbody></table></Panel></div>;
}
