"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Panel } from "@/components/ui/Panel";
import { StatsCards } from "@/components/dashboard/StatsCards";
import { PrevalenceChart } from "@/components/dashboard/PrevalenceChart";
import { RiskLevelBadge } from "@/components/dashboard/RiskLevelBadge";
import { AgeDistributionChart } from "@/components/dashboard/AgeDistributionChart";
import { BarangayRankingTable } from "@/components/dashboard/BarangayRankingTable";

export default function DashboardPage() {
  const summary = useQuery({ queryKey: ["summary"], queryFn: () => api.get("/api/dashboard/summary").then((r) => r.data) });
  const trend = useQuery({ queryKey: ["trend"], queryFn: () => api.get("/api/dashboard/prevalence-trend").then((r) => r.data) });
  const ages = useQuery({ queryKey: ["ages"], queryFn: () => api.get("/api/dashboard/age-distribution").then((r) => r.data) });
  const ranking = useQuery({ queryKey: ["ranking"], queryFn: () => api.get("/api/dashboard/barangay-comparison").then((r) => r.data), retry: false });
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between"><h1 className="text-2xl font-semibold">Dashboard</h1><RiskLevelBadge level={summary.data?.risk_level} /></div>
      <StatsCards data={summary.data} />
      <div className="grid gap-6 lg:grid-cols-2"><Panel title="Prevalence Trend"><PrevalenceChart data={trend.data || []} /></Panel><Panel title="Age Distribution"><AgeDistributionChart data={ages.data || []} /></Panel></div>
      {ranking.data && <Panel title="Barangay Ranking"><BarangayRankingTable rows={ranking.data} /></Panel>}
    </div>
  );
}
