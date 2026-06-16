"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Panel } from "@/components/ui/Panel";
import { StatsCards } from "@/components/dashboard/StatsCards";
import { PrevalenceChart } from "@/components/dashboard/PrevalenceChart";
import { RiskLevelBadge } from "@/components/dashboard/RiskLevelBadge";
import { AgeDistributionChart } from "@/components/dashboard/AgeDistributionChart";
import { BarangayRankingTable } from "@/components/dashboard/BarangayRankingTable";
import { SexBreakdownChart } from "@/components/dashboard/SexBreakdownChart";

export default function DashboardPage() {
  const summary = useQuery({ queryKey: ["summary"], queryFn: () => api.get("/api/dashboard/summary").then((r) => r.data) });
  const trend = useQuery({ queryKey: ["trend"], queryFn: () => api.get("/api/dashboard/prevalence-trend").then((r) => r.data) });
  const ages = useQuery({ queryKey: ["ages"], queryFn: () => api.get("/api/dashboard/age-distribution").then((r) => r.data) });
  const sexBreakdown = useQuery({ queryKey: ["sex-breakdown"], queryFn: () => api.get("/api/dashboard/sex-breakdown").then((r) => r.data) });
  const activity = useQuery({ queryKey: ["recent-activity"], queryFn: () => api.get("/api/logs").then((r) => r.data), retry: false });
  const ranking = useQuery({ queryKey: ["ranking"], queryFn: () => api.get("/api/dashboard/barangay-comparison").then((r) => r.data), retry: false });
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between"><h1 className="text-2xl font-semibold">Dashboard</h1><RiskLevelBadge level={summary.data?.risk_level} /></div>
      <StatsCards data={summary.data} />
      <Panel title="Risk Assessment">
        <div className="flex flex-wrap items-center gap-4">
          <RiskLevelBadge level={summary.data?.risk_level} />
          <p className="text-sm text-muted">
            Triggered by wasting, stunting, and underweight prevalence thresholds from the latest measurements.
          </p>
        </div>
      </Panel>
      <div className="grid gap-6 lg:grid-cols-2"><Panel title="Prevalence Trend"><PrevalenceChart data={trend.data || []} /></Panel><Panel title="Age Distribution"><AgeDistributionChart data={ages.data || []} /></Panel></div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Sex Breakdown"><SexBreakdownChart data={sexBreakdown.data} /></Panel>
        <Panel title="Recent Activity">
          {activity.data ? (
            <div className="space-y-3">
              {activity.data.slice(0, 10).map((entry: any) => (
                <div key={entry.id} className="rounded border border-slate-200 p-3 text-sm">
                  <p className="font-medium">{entry.action}</p>
                  <p className="text-xs text-muted">{entry.entity_type} - {new Date(entry.created_at).toLocaleString()}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted">Recent activity is available to Super Admin users.</p>
          )}
        </Panel>
      </div>
      {ranking.data && <Panel title="Barangay Ranking"><BarangayRankingTable rows={ranking.data} /></Panel>}
    </div>
  );
}
