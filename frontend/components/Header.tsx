"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, type User } from "@/lib/api";

export function Header({ user }: { user: User | null }) {
  const router = useRouter();
  async function logout() {
    await api("/auth/logout", { method: "POST" });
    router.replace("/login");
  }
  return (
    <header className="border-b border-border bg-card">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4">
        <Link href="/runs" className="text-lg font-semibold tracking-tight">
          et al.
        </Link>
        {user && (
          <div className="flex items-center gap-4 text-sm text-muted">
            <span>{user.email}</span>
            <button onClick={logout} className="hover:text-foreground">
              Sign out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
