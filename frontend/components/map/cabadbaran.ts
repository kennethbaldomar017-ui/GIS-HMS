import type { LatLngBoundsExpression, LatLngExpression } from "leaflet";

export const CABADBARAN_CENTER: LatLngExpression = [9.1833, 125.5333];

export const CABADBARAN_BOUNDS: LatLngBoundsExpression = [
  [9.09, 125.45],
  [9.27, 125.64],
];

export const CABADBARAN_MAP_OPTIONS = {
  center: CABADBARAN_CENTER,
  bounds: CABADBARAN_BOUNDS,
  maxBounds: CABADBARAN_BOUNDS,
  maxBoundsViscosity: 1,
  minZoom: 12,
  zoom: 13,
};

export const CABADBARAN_MAP_CLASS = "aspect-square w-full max-w-[640px] rounded-lg border border-slate-200";

export function isWithinCabadbaranBounds(lat: number, lng: number) {
  const [[south, west], [north, east]] = CABADBARAN_BOUNDS as [[number, number], [number, number]];

  return lat >= south && lat <= north && lng >= west && lng <= east;
}
