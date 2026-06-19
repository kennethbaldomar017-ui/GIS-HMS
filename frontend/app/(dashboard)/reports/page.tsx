"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Panel } from "@/components/ui/Panel";
import { Badge } from "@/components/ui/Badge";
import { GenerateReportForm } from "@/components/reports/GenerateReportForm";

export default function ReportsPage() {
  const q = useQuery({ queryKey: ["reports"], queryFn: () => api.get("/api/reports").then((r) => r.data) });
  return <div className="space-y-6"><h1 className="text-2xl font-semibold">Reports</h1><Panel title="Generate Report"><GenerateReportForm onSaved={() => q.refetch()} /></Panel><Panel title="Report Workflow"><table className="w-full text-left text-sm"><thead><tr className="border-b"><th className="py-2">Title</th><th>Type</th><th>Period</th><th>Status</th></tr></thead><tbody>{q.data?.map((r: any) => <tr key={r.id} className="border-b last:border-0"><td className="py-2 font-medium">{r.title}</td><td>{r.report_type}</td><td>{r.period_start} - {r.period_end}</td><td><Badge tone={r.status}>{r.status}</Badge></td></tr>)}</tbody></table></Panel></div>;
}
