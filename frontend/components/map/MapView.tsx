"use client";

import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import { useQuery } from "@tanstack/react-query";
import L from "leaflet";
import { api } from "@/lib/api";
import { CABADBARAN_MAP_CLASS, CABADBARAN_MAP_OPTIONS, isWithinCabadbaranBounds } from "./cabadbaran";

const icon = new L.Icon({ iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png", shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png", iconSize: [25, 41], iconAnchor: [12, 41] });

export function MapView() {
  const markers = useQuery({ queryKey: ["map-markers"], queryFn: () => api.get("/api/maps/child-markers").then((r) => r.data) });
  const cabadbaranMarkers = markers.data?.filter((m: any) => isWithinCabadbaranBounds(m.lat, m.lng)) || [];

  return (
    <MapContainer {...CABADBARAN_MAP_OPTIONS} className={CABADBARAN_MAP_CLASS}>
      <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {cabadbaranMarkers.map((m: any) => <Marker key={m.id} position={[m.lat, m.lng]} icon={icon}><Popup><strong>{m.name}</strong><br />{m.overall_status}<br />Last measured: {m.last_measured}</Popup></Marker>)}
    </MapContainer>
  );
}
