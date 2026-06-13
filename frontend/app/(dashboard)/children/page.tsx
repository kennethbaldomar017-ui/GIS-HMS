"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { Panel } from "@/components/ui/Panel";
import { ChildForm } from "@/components/children/ChildForm";

export default function ChildrenPage() {
  const q = useQuery({ queryKey: ["children"], queryFn: () => api.get("/api/children").then((r) => r.data) });
  return <div className="space-y-6"><h1 className="text-2xl font-semibold">Children</h1><Panel title="Add Child"><ChildForm onSaved={() => q.refetch()} /></Panel><Panel title="Records"><table className="w-full text-left text-sm"><thead><tr className="border-b"><th className="py-2">Name</th><th>Age</th><th>Sex</th><th>Status</th><th>Last Measured</th><th></th></tr></thead><tbody>{q.data?.map((c: any) => <tr key={c.id} className="border-b last:border-0"><td className="py-2 font-medium">{c.full_name}</td><td>{c.age_months}m</td><td>{c.sex}</td><td>{c.latest_measurement ? <Badge tone={c.latest_measurement.overall_status}>{c.latest_measurement.overall_status}</Badge> : "No data"}</td><td>{c.latest_measurement?.date || "-"}</td><td><Link className="text-brand" href={`/children/${c.id}`}>View</Link></td></tr>)}</tbody></table></Panel></div>;
}
