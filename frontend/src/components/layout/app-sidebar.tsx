"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Building2, Gauge, GitCompare, Layers } from "lucide-react";

import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge },
  { href: "/companies", label: "Companies", icon: Building2 },
  { href: "/comparison", label: "Comparison", icon: GitCompare },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-72 border-r border-[var(--line)] bg-[var(--surface)] p-6 lg:block">
      <div className="mb-10 flex items-center gap-3">
        <div className="rounded-lg bg-[var(--brand)] p-2 text-white">
          <BarChart3 className="h-5 w-5" />
        </div>
        <div>
          <p className="font-semibold text-[var(--ink)]">Munqith</p>
          <p className="text-xs text-[var(--muted)]">Financial Intelligence</p>
        </div>
      </div>

      <nav className="space-y-2">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-[var(--brand-soft)] text-[var(--brand-strong)]"
                  : "text-[var(--muted)] hover:bg-[var(--surface-soft)] hover:text-[var(--ink)]",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-10 rounded-xl border border-[var(--line)] bg-white p-4">
        <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">
          <Layers className="h-4 w-4" />
          Phase Status
        </p>
        <p className="mt-2 text-sm text-[var(--ink)]">Phase 2 shell is active. Auth and data wiring continue in upcoming phases.</p>
      </div>
    </aside>
  );
}
