"use client";

import dynamic from "next/dynamic";

export const DynamicMap = dynamic(() => import("./MapView").then((m) => m.MapView), { ssr: false, loading: () => <div className="grid h-[520px] place-items-center rounded-lg border border-slate-200">Loading map...</div> });
export const DynamicHeatmap = dynamic(() => import("./HeatmapView").then((m) => m.HeatmapView), { ssr: false, loading: () => <div className="grid h-[520px] place-items-center rounded-lg border border-slate-200">Loading heatmap...</div> });
