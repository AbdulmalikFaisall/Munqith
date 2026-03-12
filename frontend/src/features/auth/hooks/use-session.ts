"use client";

import { useQuery } from "@tanstack/react-query";

import { SessionDto } from "@/lib/api/types";

async function fetchSession(): Promise<SessionDto> {
  const response = await fetch("/api/auth/session", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch session");
  }
  return (await response.json()) as SessionDto;
}

export function useSession() {
  return useQuery({
    queryKey: ["auth", "session"],
    queryFn: fetchSession,
    staleTime: 15_000,
  });
}
