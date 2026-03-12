"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

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
    },
  });
}

export function useExportSnapshotPdfMutation(snapshotId: string) {
  return useMutation({
    mutationFn: () => exportPdf(snapshotId),
  });
}
