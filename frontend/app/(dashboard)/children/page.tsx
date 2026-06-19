"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { Panel } from "@/components/ui/Panel";
import { ChildForm } from "@/components/children/ChildForm";

export default function ChildrenPage() {
  const [search, setSearch] = useState("");
  const [barangayId, setBarangayId] = useState("");
  const [purokId, setPurokId] = useState("");
  const [status, setStatus] = useState("all");
  const [sex, setSex] = useState("");
  const [maxAge, setMaxAge] = useState(60);
  const q = useQuery({ queryKey: ["children", search, barangayId, purokId, sex], queryFn: () => api.get("/api/children", { params: { search: search || undefined, barangay_id: barangayId || undefined, purok_id: purokId || undefined, sex: sex || undefined } }).then((r) => r.data) });
  const barangays = useQuery({ queryKey: ["barangays"], queryFn: () => api.get("/api/barangays").then((r) => r.data), retry: false });
  const puroks = useQuery({ queryKey: ["puroks", barangayId], queryFn: () => api.get("/api/puroks", { params: { barangay_id: barangayId || undefined } }).then((r) => r.data), retry: false });

  const filteredRows = useMemo(() => {
    return (q.data || []).filter((child: any) => {
      const latestStatus = child.latest_measurement?.overall_status || "not_yet_measured";
      const statusMatches = status === "all" || latestStatus === status;
      return statusMatches && child.age_months <= maxAge;
    });
  }, [maxAge, q.data, status]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Children</h1>
        <div className="flex gap-2">
          <Link className="rounded border border-slate-300 px-3 py-2 text-sm" href="/children/import">Import via Excel</Link>
        </div>
      </div>
      <Panel title="Add Child"><ChildForm onSaved={() => q.refetch()} /></Panel>
      <Panel title="Filters">
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-6">
          <input className="rounded border px-3 py-2 text-sm lg:col-span-2" placeholder="Search child or guardian" value={search} onChange={(e) => setSearch(e.target.value)} />
          <select className="rounded border px-3 py-2 text-sm" value={barangayId} onChange={(e) => { setBarangayId(e.target.value); setPurokId(""); }}>
            <option value="">All barangays</option>
            {barangays.data?.map((b: any) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
          <select className="rounded border px-3 py-2 text-sm" value={purokId} onChange={(e) => setPurokId(e.target.value)}>
            <option value="">All puroks</option>
            {puroks.data?.map((p: any) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <select className="rounded border px-3 py-2 text-sm" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="all">All statuses</option>
            <option value="SAM">SAM</option>
            <option value="MAM">MAM</option>
            <option value="normal">Normal</option>
            <option value="not_yet_measured">Not Yet Measured</option>
          </select>
          <select className="rounded border px-3 py-2 text-sm" value={sex} onChange={(e) => setSex(e.target.value)}>
            <option value="">All sex</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </div>
        <label className="mt-4 block text-sm">
          <span className="text-muted">Maximum age: {maxAge} months</span>
          <input className="mt-2 block w-full" type="range" min={0} max={60} value={maxAge} onChange={(e) => setMaxAge(Number(e.target.value))} />
        </label>
      </Panel>
      <Panel title="Records">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead><tr className="border-b"><th className="py-2">Name</th><th>Age</th><th>Sex</th><th>Barangay</th><th>Purok</th><th>Status</th><th>Last Measured</th><th>Actions</th></tr></thead>
            <tbody>{filteredRows.map((c: any) => <tr key={c.id} className="border-b last:border-0"><td className="py-2 font-medium">{c.full_name}</td><td>{c.age_months}m</td><td>{c.sex}</td><td>{barangays.data?.find((b: any) => b.id === c.barangay_id)?.name || "-"}</td><td>{puroks.data?.find((p: any) => p.id === c.purok_id)?.name || "-"}</td><td>{c.latest_measurement ? <Badge tone={c.latest_measurement.overall_status}>{c.latest_measurement.overall_status}</Badge> : "Not yet measured"}</td><td>{c.latest_measurement?.date || "-"}</td><td className="space-x-3 whitespace-nowrap"><Link className="text-brand" href={`/children/${c.id}`}>View Profile</Link><Link className="text-brand" href={`/children/${c.id}`}>Edit</Link><Link className="text-brand" href={`/children/${c.id}`}>Add Measurement</Link><Link className="text-brand" href={`/referrals?child=${c.id}`}>Create Referral</Link></td></tr>)}</tbody>
          </table>
        </div>
        <p className="mt-3 text-sm text-muted">Showing {filteredRows.length} children.</p>
      </Panel>
    </div>
  );
}
