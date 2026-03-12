"use client";

import { useQuery } from "@tanstack/react-query";

import { CompanySummaryDto } from "@/lib/api/types";

async function fetchCompanies(): Promise<CompanySummaryDto[]> {
  const response = await fetch("/api/companies", { cache: "no-store" });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(payload?.message ?? "Failed to fetch companies");
  }
  return (await response.json()) as CompanySummaryDto[];
}

export function useCompaniesQuery() {
  return useQuery({
    queryKey: ["companies", "list"],
    queryFn: fetchCompanies,
    staleTime: 20_000,
  });
}
