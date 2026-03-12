"use client";

import { useRouter } from "next/navigation";
import { Bell, Search, ShieldCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useLogoutMutation } from "@/features/auth/hooks/use-auth-mutations";
import { useSession } from "@/features/auth/hooks/use-session";

interface TopBarProps {
  title: string;
  subtitle: string;
}

export function TopBar({ title, subtitle }: TopBarProps) {
  const router = useRouter();
  const sessionQuery = useSession();
  const logoutMutation = useLogoutMutation();

  async function handleLogout() {
    await logoutMutation.mutateAsync();
    router.push("/login");
    router.refresh();
  }

  return (
    <header className="sticky top-0 z-20 border-b border-[var(--line)] bg-white/90 px-4 py-3 backdrop-blur md:px-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold text-[var(--ink)]">{title}</h1>
          <p className="text-sm text-[var(--muted)]">{subtitle}</p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Search className="h-4 w-4" />
            Search
          </Button>
          <Button variant="outline" size="sm" aria-label="notifications">
            <Bell className="h-4 w-4" />
          </Button>
          <span className="inline-flex items-center gap-1 rounded-full bg-[var(--success-soft)] px-3 py-1 text-xs font-medium text-[var(--success-ink)]">
            <ShieldCheck className="h-3.5 w-3.5" />
            {sessionQuery.data?.role ?? "Session"}
          </span>
          <Button variant="outline" size="sm" onClick={handleLogout} disabled={logoutMutation.isPending}>
            {logoutMutation.isPending ? "Signing out..." : "Logout"}
          </Button>
        </div>
      </div>
    </header>
  );
}
