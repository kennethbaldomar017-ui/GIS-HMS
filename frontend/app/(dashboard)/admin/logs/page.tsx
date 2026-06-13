"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Panel } from "@/components/ui/Panel";

export default function LogsPage() {
  const q = useQuery({ queryKey: ["logs"], queryFn: () => api.get("/api/logs").then((r) => r.data) });
  return <div className="space-y-6"><h1 className="text-2xl font-semibold">Activity Logs</h1><Panel title="Audit Log"><table className="w-full text-left text-sm"><thead><tr className="border-b"><th className="py-2">Action</th><th>Resource</th><th>IP</th><th>Time</th></tr></thead><tbody>{q.data?.map((l: any) => <tr key={l.id} className="border-b last:border-0"><td className="py-2 font-medium">{l.action}</td><td>{l.resource_type}</td><td>{l.ip_address}</td><td>{l.created_at}</td></tr>)}</tbody></table></Panel></div>;
}
