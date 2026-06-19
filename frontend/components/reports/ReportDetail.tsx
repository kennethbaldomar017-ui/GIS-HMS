import { Badge } from "@/components/ui/Badge";

export function ReportDetail({ report }: { report: any }) {
  if (!report) return null;
  return <div className="space-y-3"><h3 className="font-semibold">{report.title}</h3><Badge tone={report.status}>{report.status}</Badge><pre className="overflow-auto rounded bg-slate-950 p-3 text-xs text-white">{JSON.stringify(report.data, null, 2)}</pre></div>;
}
