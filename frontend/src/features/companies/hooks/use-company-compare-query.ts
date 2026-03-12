"use client";

import { useQuery } from "@tanstack/react-query";

import { CompareResponseDto } from "@/lib/api/types";

async function fetchComparison(companyId: string, fromDate: string, toDate: string): Promise<CompareResponseDto> {
  const params = new URLSearchParams({ fromDate, toDate });
  const response = await fetch(`/api/companies/${companyId}/compare?${params.toString()}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(payload?.message ?? "Failed to compare snapshots");
  }

  return (await response.json()) as CompareResponseDto;
}

export function useCompanyCompareQuery(companyId: string, fromDate: string, toDate: string) {
  return useQuery({
    queryKey: ["companies", "compare", companyId, fromDate, toDate],
    queryFn: () => fetchComparison(companyId, fromDate, toDate),
    enabled: Boolean(companyId && fromDate && toDate),
    staleTime: 10_000,
  });
}
