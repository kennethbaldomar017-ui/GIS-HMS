"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Panel } from "@/components/ui/Panel";

function formatAction(action: string) {
  return action.replace(/_/g, " ");
}

export default function LogsPage() {
  const [action, setAction] = useState("");
  const [logDate, setLogDate] = useState("");

  const actions = useQuery({
    queryKey: ["log-actions"],
    queryFn: () => api.get("/api/logs/actions").then((r) => r.data),
  });

  const logs = useQuery({
    queryKey: ["logs", action, logDate],
    queryFn: () =>
      api
        .get("/api/logs", {
          params: {
            action: action || undefined,
            log_date: logDate || undefined,
          },
        })
        .then((r) => r.data),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Activity Logs</h1>
      <Panel title="Filters">
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <label className="space-y-1 text-sm">
            <span className="text-muted">Date</span>
            <input
              className="w-full rounded border px-3 py-2 text-sm"
              type="date"
              value={logDate}
              onChange={(e) => setLogDate(e.target.value)}
            />
          </label>
          <label className="space-y-1 text-sm">
            <span className="text-muted">Activity</span>
            <select
              className="w-full rounded border px-3 py-2 text-sm"
              value={action}
              onChange={(e) => setAction(e.target.value)}
            >
              <option value="">All activities</option>
              {actions.data?.map((item: string) => (
                <option key={item} value={item}>{formatAction(item)}</option>
              ))}
            </select>
          </label>
          <div className="flex items-end">
            <button
              className="rounded border border-slate-300 px-3 py-2 text-sm"
              type="button"
              onClick={() => {
                setAction("");
                setLogDate("");
              }}
            >
              Clear filters
            </button>
          </div>
        </div>
      </Panel>
      <Panel title="Audit Log">
        {logs.isLoading ? (
          <p className="text-sm text-muted">Loading logs...</p>
        ) : logs.data?.length ? (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b">
                <th className="py-2">Action</th>
                <th>Resource</th>
                <th>IP</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {logs.data.map((log: any) => (
                <tr key={log.id} className="border-b last:border-0">
                  <td className="py-2 font-medium">{formatAction(log.action)}</td>
                  <td>{log.resource_type}</td>
                  <td>{log.ip_address || "—"}</td>
                  <td>{new Date(log.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-sm text-muted">No activity logs match the selected filters.</p>
        )}
      </Panel>
    </div>
  );
}
