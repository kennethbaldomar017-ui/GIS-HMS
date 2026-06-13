import { Badge } from "@/components/ui/Badge";

export function BarangayRankingTable({ rows }: { rows: any[] }) {
  return <table className="w-full text-left text-sm"><thead><tr className="border-b"><th className="py-2">Barangay</th><th>Wasting%</th><th>Stunting%</th><th>Underweight%</th><th>Risk</th></tr></thead><tbody>{rows?.map((r) => <tr key={r.barangay_id} className="border-b last:border-0"><td className="py-2 font-medium">{r.barangay}</td><td>{r.wasting_rate}</td><td>{r.stunting_rate}</td><td>{r.underweight_rate}</td><td><Badge tone={r.risk_level}>{r.risk_level}</Badge></td></tr>)}</tbody></table>;
}
