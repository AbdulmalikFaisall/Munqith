import Link from "next/link";

import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { SignupForm } from "@/features/auth/components/signup-form";

export default function SignupPage() {
  return (
    <main className="min-h-screen bg-[var(--surface)] px-4 py-12">
      <div className="mx-auto max-w-md">
        <Card className="space-y-4">
          <span className="inline-block rounded-full bg-[var(--brand-soft)] px-2 py-1 text-xs font-semibold text-[var(--brand-strong)]">
            Account Setup
          </span>
          <CardTitle>Create Your Munqith Account</CardTitle>
          <CardDescription>Create your first ANALYST account to access the intelligence workspace.</CardDescription>
          <SignupForm />
          <p className="text-sm text-[var(--muted)]">
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-[var(--brand-strong)] underline">
              Sign in
            </Link>
          </p>
        </Card>
      </div>
    </main>
  );
}
