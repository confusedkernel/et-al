"use client";

import { use, useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { StatusBadge } from "@/components/StatusBadge";
import { api, type Run } from "@/lib/api";
import { useUser } from "@/lib/useUser";

const LIVE = new Set<Run["status"]>(["queued", "running", "awaiting_input"]);

export default function RunPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const user = useUser();
  const [run, setRun] = useState<Run | null>(null);

  // Polling stands in until the SSE event stream lands in milestone 2.
  useEffect(() => {
    if (!user) return;
    let timer: ReturnType<typeof setTimeout>;
    const load = async () => {
      const r = await api<Run>(`/runs/${id}`);
      setRun(r);
      if (LIVE.has(r.status)) timer = setTimeout(load, 2000);
    };
    load();
    return () => clearTimeout(timer);
  }, [id, user]);

  async function cancel() {
    setRun(await api<Run>(`/runs/${id}/cancel`, { method: "POST" }));
  }

  return (
    <>
      <Header user={user} />
      <main className="mx-auto max-w-5xl space-y-6 px-4 py-8">
        {run && (
          <>
            <div className="flex items-start gap-4">
              <h1 className="flex-1 text-xl font-semibold">{run.question}</h1>
              <StatusBadge status={run.status} />
            </div>
            <div className="flex items-center gap-6 text-sm text-muted">
              <span>Phase: {run.phase}</span>
              <span className="font-mono">
                ${run.cost_usd.toFixed(2)} / ${run.budget_usd.toFixed(2)}
              </span>
              {LIVE.has(run.status) && (
                <button onClick={cancel} className="ml-auto text-red-600 hover:underline">
                  Cancel run
                </button>
              )}
            </div>
            {run.error && <p className="rounded-md bg-red-500/10 p-3 text-sm text-red-600">{run.error}</p>}
            <article className="whitespace-pre-wrap rounded-xl border border-border bg-card p-5 text-sm">
              {run.report_md ?? <span className="text-muted">Report will appear here.</span>}
            </article>
          </>
        )}
      </main>
    </>
  );
}
