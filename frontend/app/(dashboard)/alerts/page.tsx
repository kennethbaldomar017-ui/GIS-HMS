"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Panel } from "@/components/ui/Panel";
import { Badge } from "@/components/ui/Badge";

export default function AlertsPage() {
  const q = useQuery({ queryKey: ["alerts"], queryFn: () => api.get("/api/alerts?is_resolved=false").then((r) => r.data) });
  async function resolve(id: string) { await api.put(`/api/alerts/${id}/resolve`, {}); q.refetch(); }
  return <div className="space-y-6"><h1 className="text-2xl font-semibold">Alerts</h1><Panel title="Unresolved Alerts"><div className="grid gap-3">{q.data?.map((a: any) => <article key={a.id} className="rounded border p-3"><div className="flex items-center justify-between"><Badge tone={a.severity}>{a.severity}</Badge><button onClick={() => resolve(a.id)} className="rounded border px-3 py-1 text-sm">Resolve</button></div><p className="mt-2 text-sm">{a.message}</p></article>)}</div></Panel></div>;
}
