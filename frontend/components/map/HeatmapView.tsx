"use client";

import { useQuery } from "@tanstack/react-query";
import L from "leaflet";
import { GeoJSON, MapContainer, Popup, TileLayer } from "react-leaflet";
import { api } from "@/lib/api";
import { CABADBARAN_MAP_CLASS, CABADBARAN_MAP_OPTIONS } from "./cabadbaran";

type BarangaySeverity = {
  alert_count: number;
  malnutrition_count: number;
  moderate_count: number;
  name: string;
  prevalence_rate: number;
  risk_level: "critical" | "high" | "medium" | "low";
  severe_count: number;
  total_children: number;
};

type BarangayFeature = {
  properties: BarangaySeverity;
};

const riskStyles = {
  critical: { fillColor: "#dc2626", color: "#991b1b" },
  high: { fillColor: "#f97316", color: "#9a3412" },
  medium: { fillColor: "#facc15", color: "#a16207" },
  low: { fillColor: "#22c55e", color: "#15803d" },
};

function styleBarangay(feature?: BarangayFeature) {
  const risk = feature?.properties.risk_level || "low";
  const colors = riskStyles[risk];

  return {
    color: colors.color,
    fillColor: colors.fillColor,
    fillOpacity: 0.72,
    opacity: 0.95,
    weight: 2,
  };
}

function bindBarangayPopup(feature: BarangayFeature, layer: L.Layer) {
  const props = feature.properties;

  layer.bindPopup(`
    <strong>${props.name}</strong><br />
    Risk: ${props.risk_level}<br />
    Malnutrition rate: ${props.prevalence_rate}%<br />
    Malnourished children: ${props.malnutrition_count}<br />
    Severe: ${props.severe_count}<br />
    Moderate: ${props.moderate_count}<br />
    Total measured: ${props.total_children}
  `);
}

export function HeatmapView() {
  const choropleth = useQuery({
    queryKey: ["barangay-severity-heatmap"],
    queryFn: () => api.get("/api/maps/barangay-choropleth").then((r) => r.data),
  });

  return (
    <div className="space-y-3">
      <MapContainer {...CABADBARAN_MAP_OPTIONS} className={CABADBARAN_MAP_CLASS}>
        <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {choropleth.data && <GeoJSON key={JSON.stringify(choropleth.data)} data={choropleth.data} style={styleBarangay} onEachFeature={bindBarangayPopup as any} />}
      </MapContainer>
      <div className="flex max-w-[640px] flex-wrap gap-3 rounded border border-slate-200 bg-white p-3 text-xs text-slate-700">
        <span className="inline-flex items-center gap-2"><span className="h-3 w-3 rounded-sm bg-green-500" />Low</span>
        <span className="inline-flex items-center gap-2"><span className="h-3 w-3 rounded-sm bg-yellow-400" />Medium</span>
        <span className="inline-flex items-center gap-2"><span className="h-3 w-3 rounded-sm bg-orange-500" />High</span>
        <span className="inline-flex items-center gap-2"><span className="h-3 w-3 rounded-sm bg-red-600" />Critical</span>
      </div>
    </div>
  );
}
