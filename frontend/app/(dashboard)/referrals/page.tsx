"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Panel } from "@/components/ui/Panel";
import { Badge } from "@/components/ui/Badge";
import { ReferralForm } from "@/components/referrals/ReferralForm";

export default function ReferralsPage() {
  const q = useQuery({ queryKey: ["referrals"], queryFn: () => api.get("/api/referrals").then((r) => r.data) });
  return <div className="space-y-6"><h1 className="text-2xl font-semibold">Referrals</h1><Panel title="Create Referral"><ReferralForm onSaved={() => q.refetch()} /></Panel><Panel title="Referral Queue"><table className="w-full text-left text-sm"><thead><tr className="border-b"><th className="py-2">Child</th><th>Facility</th><th>Reason</th><th>Priority</th><th>Status</th><th>Date</th></tr></thead><tbody>{q.data?.map((r: any) => <tr key={r.id} className="border-b last:border-0"><td className="py-2">{r.child_id}</td><td>{r.referred_to}</td><td>{r.reason}</td><td><Badge tone={r.priority}>{r.priority}</Badge></td><td><Badge tone={r.status}>{r.status}</Badge></td><td>{r.referred_at}</td></tr>)}</tbody></table></Panel></div>;
}
