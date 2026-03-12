import Link from "next/link";

import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { LoginForm } from "@/features/auth/components/login-form";

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
            Sign in with your analyst or admin account to access the intelligence workspace.
          </CardDescription>
          <LoginForm />
          <div>
            <Link href="/dashboard" className="text-xs text-[var(--muted)] underline">
              Developer bypass: /dashboard (only when NEXT_PUBLIC_DEV_BYPASS_AUTH=true)
            </Link>
          </div>
        </Card>
      </div>
    </main>
  );
}
