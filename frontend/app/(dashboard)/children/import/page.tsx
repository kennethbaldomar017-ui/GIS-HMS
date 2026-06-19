"use client";

import { useState } from "react";
import { api, API_URL } from "@/lib/api";
import { Panel } from "@/components/ui/Panel";

export default function ImportPage() {
  const [job, setJob] = useState("");
  async function upload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    const res = await api.post("/api/import/upload", form);
    setJob(res.data.job_id);
  }
  return <div className="space-y-6"><h1 className="text-2xl font-semibold">Bulk Import</h1><Panel title="Import Children"><a className="rounded border px-3 py-2 text-sm" href={`${API_URL}/api/import/template`}>Download Template</a><input className="mt-4 block rounded border p-8" type="file" onChange={upload} />{job && <p className="mt-3 text-sm">Created import job: {job}</p>}</Panel></div>;
}
