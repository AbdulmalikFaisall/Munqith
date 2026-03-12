"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { CreateSnapshotRequestDto, SnapshotMutationResponseDto } from "@/lib/api/types";

async function createSnapshot(payload: CreateSnapshotRequestDto): Promise<SnapshotMutationResponseDto> {
  const response = await fetch("/api/snapshots", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(payload?.message ?? "Failed to create snapshot");
  }

  return (await response.json()) as SnapshotMutationResponseDto;
}

async function finalizeSnapshot(snapshotId: string): Promise<SnapshotMutationResponseDto> {
  const response = await fetch(`/api/snapshots/${snapshotId}/finalize`, {
    method: "POST",
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(payload?.message ?? "Failed to finalize snapshot");
  }

  return (await response.json()) as SnapshotMutationResponseDto;
}

async function invalidateSnapshot(snapshotId: string, reason: string): Promise<void> {
  const response = await fetch(`/api/snapshots/${snapshotId}/invalidate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ reason }),
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(payload?.message ?? "Failed to invalidate snapshot");
  }
}

async function exportPdf(snapshotId: string): Promise<void> {
  const response = await fetch(`/api/snapshots/${snapshotId}/export/pdf`, { method: "GET" });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(payload?.message ?? "Failed to export PDF");
  }

  const blob = await response.blob();
  const disposition = response.headers.get("content-disposition") ?? "";
  const filenameMatch = disposition.match(/filename=([^;]+)/i);
  const fallbackName = `snapshot_${snapshotId}.pdf`;
  const filename = filenameMatch?.[1]?.replaceAll('"', "") || fallbackName;

  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(url);
}

export function useInvalidateSnapshotMutation(snapshotId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (reason: string) => invalidateSnapshot(snapshotId, reason),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["snapshots", "detail", snapshotId] });
      await queryClient.invalidateQueries({ queryKey: ["companies"] });
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useCreateSnapshotMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateSnapshotRequestDto) => createSnapshot(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["companies"] });
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useFinalizeSnapshotMutation(snapshotId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => finalizeSnapshot(snapshotId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["snapshots", "detail", snapshotId] });
      await queryClient.invalidateQueries({ queryKey: ["companies"] });
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useExportSnapshotPdfMutation(snapshotId: string) {
  return useMutation({
    mutationFn: () => exportPdf(snapshotId),
  });
}
