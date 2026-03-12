"use client";

import { useQuery } from "@tanstack/react-query";

import { DashboardSummaryDto } from "@/lib/api/types";

async function fetchDashboardSummary(companyId: string): Promise<DashboardSummaryDto> {
  const params = new URLSearchParams({ companyId });
  const response = await fetch(`/api/analytics/dashboard?${params.toString()}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(payload?.message ?? "Failed to load dashboard summary");
  }

  return (await response.json()) as DashboardSummaryDto;
}

export function useDashboardQuery(companyId: string | null) {
  return useQuery({
    queryKey: ["dashboard", "summary", companyId],
    queryFn: () => fetchDashboardSummary(companyId as string),
    enabled: Boolean(companyId),
    staleTime: 20_000,
  });
}
