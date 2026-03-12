"use client";

import { useQuery } from "@tanstack/react-query";

import { CompanyIntelligenceDto } from "@/lib/api/types";

async function fetchCompanyIntelligence(companyId: string): Promise<CompanyIntelligenceDto> {
  const response = await fetch(`/api/companies/${companyId}`, { cache: "no-store" });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(payload?.message ?? "Failed to fetch company intelligence");
  }
  return (await response.json()) as CompanyIntelligenceDto;
}

export function useCompanyIntelligenceQuery(companyId: string) {
  return useQuery({
    queryKey: ["companies", "intelligence", companyId],
    queryFn: () => fetchCompanyIntelligence(companyId),
    enabled: Boolean(companyId),
    staleTime: 20_000,
  });
}
