"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { useRegisterMutation } from "@/features/auth/hooks/use-auth-mutations";

export function SignupForm() {
  const router = useRouter();
  const registerMutation = useRegisterMutation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await registerMutation.mutateAsync({ email, password });
    router.push("/dashboard");
    router.refresh();
  }

  return (
    <form className="space-y-4" onSubmit={onSubmit}>
      <div className="space-y-1">
        <label htmlFor="email" className="text-sm font-medium text-[var(--ink)]">
          Email
        </label>
        <input
          id="email"
          type="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="h-10 w-full rounded-md border border-[var(--line)] bg-white px-3 text-sm outline-none ring-[var(--brand)] focus:ring-2"
        />
      </div>

      <div className="space-y-1">
        <label htmlFor="password" className="text-sm font-medium text-[var(--ink)]">
          Password
        </label>
        <input
          id="password"
          type="password"
          required
          minLength={8}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="h-10 w-full rounded-md border border-[var(--line)] bg-white px-3 text-sm outline-none ring-[var(--brand)] focus:ring-2"
        />
        <p className="text-xs text-[var(--muted)]">Use at least 8 characters.</p>
      </div>

      {registerMutation.error ? <p className="text-sm text-rose-700">{registerMutation.error.message}</p> : null}

      <Button type="submit" disabled={registerMutation.isPending}>
        {registerMutation.isPending ? "Creating account..." : "Create account"}
      </Button>
    </form>
  );
}
