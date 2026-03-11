import Link from "next/link";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";

export default function LoginPage() {
  return (
    <main className="min-h-screen bg-[var(--surface)] px-4 py-12">
      <div className="mx-auto max-w-md">
        <Card className="space-y-4">
          <span className="inline-block rounded-full bg-[var(--brand-soft)] px-2 py-1 text-xs font-semibold text-[var(--brand-strong)]">
            Phase 2
          </span>
          <CardTitle>Munqith Access Portal</CardTitle>
          <CardDescription>
            Login wiring lands in Phase 3. This screen is in place for route structure and auth flow integration.
          </CardDescription>
          <div className="flex gap-2">
            <Button disabled>Sign in (Phase 3)</Button>
            <Link
              href="/dashboard"
              className={cn(
                "inline-flex h-10 items-center justify-center rounded-md border border-[var(--line)] px-4 py-2 text-sm font-medium text-[var(--ink)] transition-colors hover:bg-[var(--surface-soft)]",
              )}
            >
              Preview Shell
            </Link>
          </div>
        </Card>
      </div>
    </main>
  );
}
