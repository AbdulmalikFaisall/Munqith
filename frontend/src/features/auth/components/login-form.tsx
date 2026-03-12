"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { useLoginMutation } from "@/features/auth/hooks/use-auth-mutations";
import { Button } from "@/components/ui/button";

export function LoginForm() {
  const router = useRouter();
  const loginMutation = useLoginMutation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await loginMutation.mutateAsync({ email, password });
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
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="h-10 w-full rounded-md border border-[var(--line)] bg-white px-3 text-sm outline-none ring-[var(--brand)] focus:ring-2"
        />
      </div>

      {loginMutation.error ? (
        <p className="text-sm text-rose-700">{loginMutation.error.message}</p>
      ) : null}

      <Button type="submit" disabled={loginMutation.isPending}>
        {loginMutation.isPending ? "Signing in..." : "Sign in"}
      </Button>
    </form>
  );
}
