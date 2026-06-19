"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Building2, MapPinned, Plus } from "lucide-react";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { Panel } from "@/components/ui/Panel";

export default function BarangayManagementPage() {
  const [selectedId, setSelectedId] = useState("");
  const [search, setSearch] = useState("");
  const barangays = useQuery({ queryKey: ["barangays"], queryFn: () => api.get("/api/barangays").then((r) => r.data) });
  const puroks = useQuery({ queryKey: ["puroks"], queryFn: () => api.get("/api/puroks").then((r) => r.data) });
  const children = useQuery({ queryKey: ["children-admin"], queryFn: () => api.get("/api/children").then((r) => r.data) });
  const users = useQuery({ queryKey: ["users"], queryFn: () => api.get("/api/users").then((r) => r.data), retry: false });

  const rows = useMemo(() => {
    return (barangays.data || []).map((barangay: any) => {
      const barangayPuroks = (puroks.data || []).filter((p: any) => p.barangay_id === barangay.id);
      const barangayChildren = (children.data || []).filter((c: any) => c.barangay_id === barangay.id);
      const assignedAdmin = (users.data || []).find((u: any) => u.barangay_id === barangay.id);
      return { ...barangay, purok_count: barangayPuroks.length, child_count: barangayChildren.length, assigned_admin: assignedAdmin };
    });
  }, [barangays.data, children.data, puroks.data, users.data]);

  const filteredRows = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return rows;
    return rows.filter((row: any) =>
      row.name.toLowerCase().includes(query) ||
      row.code.toLowerCase().includes(query) ||
      row.assigned_admin?.username?.toLowerCase().includes(query)
    );
  }, [rows, search]);

  const selected = filteredRows.find((row: any) => row.id === selectedId) || filteredRows[0] || rows.find((row: any) => row.id === selectedId) || rows[0];
  const selectedPuroks = (puroks.data || []).filter((p: any) => p.barangay_id === selected?.id);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Barangay Management</h1>
          <p className="text-sm text-muted">Manage the 15 barangays, assigned admins, and purok coverage.</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded border border-slate-300 px-3 py-2 text-sm">
          <Plus className="h-4 w-4" /> Add Barangay
        </button>
      </div>

      <Panel title="Barangays">
        <input
          className="mb-4 w-full rounded border px-3 py-2 text-sm md:max-w-sm"
          placeholder="Search barangay, code, or admin"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b">
                <th className="py-2">Barangay Name</th>
                <th>Code</th>
                <th>Purok Count</th>
                <th>Registered Children</th>
                <th>Assigned Admin</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredRows.map((row: any) => (
                <tr key={row.id} className="border-b last:border-0">
                  <td className="py-2 font-medium">{row.name}</td>
                  <td>{row.code}</td>
                  <td>{row.purok_count}</td>
                  <td>{row.child_count}</td>
                  <td>{row.assigned_admin?.username || <span className="text-muted">Unassigned</span>}</td>
                  <td className="space-x-3">
                    <button onClick={() => setSelectedId(row.id)} className="text-brand">View</button>
                    <button className="text-brand">Edit</button>
                    <button onClick={() => setSelectedId(row.id)} className="text-brand">Manage Puroks</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      {selected && (
        <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
          <Panel title="Barangay Detail">
            <div className="mb-4 flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <Building2 className="h-5 w-5 text-brand" />
                  <h2 className="text-lg font-semibold">{selected.name}</h2>
                </div>
                <p className="mt-1 text-sm text-muted">Code {selected.code} - Population {selected.population_count || "Not set"}</p>
              </div>
              <Badge tone={selected.assigned_admin ? "approved" : "pending"}>{selected.assigned_admin ? "Assigned" : "Needs Admin"}</Badge>
            </div>
            <table className="w-full text-left text-sm">
              <thead><tr className="border-b"><th className="py-2">Purok Name</th><th>Code</th><th>Child Count</th><th>Actions</th></tr></thead>
              <tbody>
                {selectedPuroks.map((purok: any) => (
                  <tr key={purok.id} className="border-b last:border-0">
                    <td className="py-2 font-medium">{purok.name}</td>
                    <td>{purok.code}</td>
                    <td>{(children.data || []).filter((c: any) => c.purok_id === purok.id).length}</td>
                    <td className="space-x-3"><button className="text-brand">Edit</button><button className="text-red-600">Delete</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panel>
          <div className="space-y-6">
            <Panel title="Assigned Admin">
              <p className="font-medium">{selected.assigned_admin?.username || "No admin assigned"}</p>
              <p className="text-sm text-muted">{selected.assigned_admin?.email || "Assign a barangay admin from User Management."}</p>
              <button className="mt-4 rounded border border-slate-300 px-3 py-2 text-sm">Reassign</button>
            </Panel>
            <Panel title="Map Preview">
              <div className="flex h-48 items-center justify-center rounded border border-dashed border-slate-300 bg-slate-50 text-sm text-muted">
                <MapPinned className="mr-2 h-4 w-4" /> Polygon preview uses uploaded GeoJSON.
              </div>
            </Panel>
          </div>
        </div>
      )}
    </div>
  );
}
