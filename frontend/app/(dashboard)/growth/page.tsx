"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Panel } from "@/components/ui/Panel";
import { WHOGrowthChart } from "@/components/growth/WHOGrowthChart";
import { ZScoreSummaryCard } from "@/components/growth/ZScoreSummaryCard";

export default function GrowthPage() {
  const [childId, setChildId] = useState("");
  const children = useQuery({ queryKey: ["children"], queryFn: () => api.get("/api/children").then((r) => r.data) });
  const growth = useQuery({ queryKey: ["growth", childId], queryFn: () => api.get(`/api/children/${childId}/measurements`).then((r) => r.data), enabled: !!childId });
  const latest = growth.data?.[0];
  return <div className="space-y-6"><h1 className="text-2xl font-semibold">Growth Monitoring</h1><select className="rounded border px-3 py-2" onChange={(e) => setChildId(e.target.value)}><option>Select child</option>{children.data?.map((c: any) => <option key={c.id} value={c.id}>{c.full_name}</option>)}</select><ZScoreSummaryCard measurement={latest} /><Panel title="WHO Growth Chart"><WHOGrowthChart data={growth.data || []} /></Panel></div>;
}
