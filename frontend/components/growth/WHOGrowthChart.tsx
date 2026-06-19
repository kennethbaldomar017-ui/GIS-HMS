"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, ReferenceLine } from "recharts";

export function WHOGrowthChart({ data }: { data: any[] }) {
  return <ResponsiveContainer width="100%" height={360}><LineChart data={data}><XAxis dataKey="age_in_months" /><YAxis domain={[-6, 6]} /><Tooltip /><ReferenceLine y={-3} stroke="#dc2626" /><ReferenceLine y={-2} stroke="#d97706" /><ReferenceLine y={0} stroke="#16a34a" /><ReferenceLine y={2} stroke="#d97706" /><ReferenceLine y={3} stroke="#dc2626" /><Line dataKey="whz" stroke="#0f766e" /></LineChart></ResponsiveContainer>;
}
