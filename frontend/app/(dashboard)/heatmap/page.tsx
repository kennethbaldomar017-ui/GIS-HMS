import { DynamicHeatmap } from "@/components/map/MapContainer";
import { MapControls } from "@/components/map/MapControls";
import { MapSidebar } from "@/components/map/MapSidebar";

export default function HeatmapPage() {
  return <div className="grid gap-4 lg:grid-cols-[1fr_280px]"><section><h1 className="mb-4 text-2xl font-semibold">Cabadbaran City Heatmap</h1><DynamicHeatmap /></section><div className="space-y-4"><MapControls /><MapSidebar /></div></div>;
}
