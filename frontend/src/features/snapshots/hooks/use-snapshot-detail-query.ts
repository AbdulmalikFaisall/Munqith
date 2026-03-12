"use client";

import { useQuery } from "@tanstack/react-query";

import { SnapshotDetailDto } from "@/lib/api/types";

async function fetchSnapshot(snapshotId: string): Promise<SnapshotDetailDto> {
  const response = await fetch(`/api/snapshots/${snapshotId}`, { cache: "no-store" });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(payload?.message ?? "Failed to fetch snapshot details");
  }
  return (await response.json()) as SnapshotDetailDto;
}

export function useSnapshotDetailQuery(snapshotId: string) {
  return useQuery({
    queryKey: ["snapshots", "detail", snapshotId],
    queryFn: () => fetchSnapshot(snapshotId),
    enabled: Boolean(snapshotId),
    staleTime: 20_000,
  });
}
