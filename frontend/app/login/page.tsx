"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await api(`/auth/${mode}`, { method: "POST", body: JSON.stringify({ email, password }) });
      router.replace("/runs");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <form onSubmit={submit} className="w-full max-w-sm space-y-4 rounded-xl border border-border bg-card p-6 shadow-sm">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">et al.</h1>
          <p className="text-sm text-muted">{mode === "login" ? "Sign in to your instance" : "Create an account"}</p>
        </div>
        <input
          type="email"
          required
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        />
        <input
          type="password"
          required
          minLength={8}
          placeholder="Password (8+ characters)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          disabled={busy}
          className="w-full rounded-md bg-accent px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {mode === "login" ? "Sign in" : "Create account"}
        </button>
        <button
          type="button"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
          className="w-full text-center text-sm text-muted hover:text-foreground"
        >
          {mode === "login" ? "No account? Register" : "Have an account? Sign in"}
        </button>
      </form>
    </main>
  );
}
