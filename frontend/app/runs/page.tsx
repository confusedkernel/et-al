"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { StatusBadge } from "@/components/StatusBadge";
import { api, type Run } from "@/lib/api";
import { useUser } from "@/lib/useUser";

export default function RunsPage() {
  const user = useUser();
  const router = useRouter();
  const [runs, setRuns] = useState<Run[]>([]);
  const [question, setQuestion] = useState("");
  const [budget, setBudget] = useState(1);
  const [experiments, setExperiments] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) api<Run[]>("/runs").then(setRuns);
  }, [user]);

  async function create(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const run = await api<Run>("/runs", {
        method: "POST",
        body: JSON.stringify({ question, budget_usd: budget, run_experiments: experiments }),
      });
      router.push(`/runs/${run.id}`);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <>
      <Header user={user} />
      <main className="mx-auto max-w-5xl space-y-8 px-4 py-8">
        <form onSubmit={create} className="space-y-3 rounded-xl border border-border bg-card p-5 shadow-sm">
          <h2 className="font-medium">New research run</h2>
          <textarea
            required
            minLength={10}
            rows={3}
            placeholder="What do you want to investigate? e.g. Which data augmentation methods most improve small-dataset image classification?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          />
          <div className="flex flex-wrap items-center gap-x-6 gap-y-3 text-sm">
            <label className="flex items-center gap-2">
              Budget $
              <input
                type="number"
                min={0.1}
                step={0.1}
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                className="w-20 rounded-md border border-border bg-background px-2 py-1"
              />
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={experiments} onChange={(e) => setExperiments(e.target.checked)} />
              Run experiments after literature review
            </label>
            <button className="ml-auto rounded-md bg-accent px-4 py-2 font-medium text-white">Start run</button>
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </form>

        <section className="space-y-2">
          <h2 className="font-medium">Runs</h2>
          {runs.length === 0 && <p className="text-sm text-muted">No runs yet.</p>}
          <ul className="divide-y divide-border rounded-xl border border-border bg-card">
            {runs.map((run) => (
              <li key={run.id}>
                <Link href={`/runs/${run.id}`} className="flex items-center gap-4 px-4 py-3 hover:bg-background">
                  <span className="flex-1 truncate text-sm">{run.question}</span>
                  <span className="font-mono text-xs text-muted">${run.cost_usd.toFixed(2)}</span>
                  <StatusBadge status={run.status} />
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </main>
    </>
  );
}
