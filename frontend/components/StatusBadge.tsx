import type { Run } from "@/lib/api";

const STYLES: Record<Run["status"], string> = {
  queued: "bg-stone-500/15 text-stone-600 dark:text-stone-300",
  running: "bg-indigo-500/15 text-indigo-600 dark:text-indigo-300",
  awaiting_input: "bg-amber-500/15 text-amber-700 dark:text-amber-300",
  completed: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
  failed: "bg-red-500/15 text-red-700 dark:text-red-300",
  cancelled: "bg-stone-500/15 text-stone-500",
};

export function StatusBadge({ status }: { status: Run["status"] }) {
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STYLES[status]}`}>{status.replace("_", " ")}</span>
  );
}
