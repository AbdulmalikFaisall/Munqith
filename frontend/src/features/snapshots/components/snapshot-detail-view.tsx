"use client";

import { FormEvent, useMemo, useState } from "react";

import { MetricCard } from "@/components/intelligence/metric-card";
import { StageBadge } from "@/components/intelligence/stage-badge";
import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { SkeletonCard } from "@/components/states/skeleton-card";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  useExportSnapshotPdfMutation,
  useInvalidateSnapshotMutation,
} from "@/features/snapshots/hooks/use-snapshot-actions";
import { useSnapshotDetailQuery } from "@/features/snapshots/hooks/use-snapshot-detail-query";
import { useSession } from "@/features/auth/hooks/use-session";

interface SnapshotDetailViewProps {
  snapshotId: string;
}

function valueToText(value: unknown): string {
  if (value === null || value === undefined) {
    return "N/A";
  }
  if (typeof value === "number") {
    return value.toLocaleString();
  }
  return String(value);
}

export function SnapshotDetailView({ snapshotId }: SnapshotDetailViewProps) {
  const sessionQuery = useSession();
  const detailQuery = useSnapshotDetailQuery(snapshotId);
  const exportPdfMutation = useExportSnapshotPdfMutation(snapshotId);
  const invalidateMutation = useInvalidateSnapshotMutation(snapshotId);
  const [reason, setReason] = useState("");

  const isAdmin = sessionQuery.data?.role === "ADMIN";

  const topMetrics = useMemo(() => {
    const data = detailQuery.data;
    if (!data) {
      return null;
    }

    return {
      stage: valueToText(data.stage),
      runway: typeof data.runway_months === "number" ? `${data.runway_months.toFixed(2)} months` : "N/A",
      burn: valueToText(data.monthly_burn),
      revenue: valueToText(data.monthly_revenue),
      status: valueToText(data.status),
      snapshotDate: valueToText(data.snapshot_date),
      companyId: valueToText(data.company_id),
    };
  }, [detailQuery.data]);

  async function onInvalidate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await invalidateMutation.mutateAsync(reason);
    setReason("");
    await detailQuery.refetch();
  }

  if (detailQuery.isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (detailQuery.isError) {
    return (
      <ErrorState
        title="Unable to load snapshot details"
        description={detailQuery.error.message}
        onRetry={() => detailQuery.refetch()}
      />
    );
  }

  if (!detailQuery.data || !topMetrics) {
    return <EmptyState title="Snapshot not available" description="No detail payload was returned for this snapshot." />;
  }

  const signals = Array.isArray(detailQuery.data.signals) ? detailQuery.data.signals : [];
  const ruleResults = Array.isArray(detailQuery.data.rule_results) ? detailQuery.data.rule_results : [];
  const contributingSignals = Array.isArray(detailQuery.data.contributing_signals)
    ? detailQuery.data.contributing_signals
    : [];

  return (
    <div className="space-y-6">
      <section className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[var(--line)] bg-white p-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-[var(--muted)]">Snapshot</p>
          <p className="text-sm text-[var(--muted)]">ID: {snapshotId}</p>
          <p className="text-sm text-[var(--muted)]">Company: {topMetrics.companyId}</p>
        </div>
        <div className="flex items-center gap-2">
          <StageBadge stage={topMetrics.stage === "N/A" ? null : topMetrics.stage} />
          <span className="rounded-full bg-[var(--surface-soft)] px-3 py-1 text-xs font-medium text-[var(--ink)]">
            {topMetrics.status}
          </span>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Snapshot Date" value={topMetrics.snapshotDate} />
        <MetricCard label="Runway" value={topMetrics.runway} />
        <MetricCard label="Monthly Burn" value={topMetrics.burn} />
        <MetricCard label="Monthly Revenue" value={topMetrics.revenue} />
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <Card className="space-y-3">
          <h3 className="text-base font-semibold text-[var(--ink)]">Export Actions</h3>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => exportPdfMutation.mutate()} disabled={exportPdfMutation.isPending}>
              {exportPdfMutation.isPending ? "Preparing PDF..." : "Download PDF"}
            </Button>
          </div>
          {exportPdfMutation.error ? (
            <p className="text-sm text-rose-700">{exportPdfMutation.error.message}</p>
          ) : null}
        </Card>

        <Card className="space-y-3">
          <h3 className="text-base font-semibold text-[var(--ink)]">Invalidate Snapshot</h3>
          {isAdmin ? (
            <form className="space-y-3" onSubmit={onInvalidate}>
              <textarea
                value={reason}
                onChange={(event) => setReason(event.target.value)}
                required
                minLength={3}
                placeholder="Enter invalidation reason"
                className="min-h-24 w-full rounded-md border border-[var(--line)] bg-white p-3 text-sm outline-none ring-[var(--brand)] focus:ring-2"
              />
              <Button type="submit" disabled={invalidateMutation.isPending}>
                {invalidateMutation.isPending ? "Invalidating..." : "Invalidate"}
              </Button>
              {invalidateMutation.error ? (
                <p className="text-sm text-rose-700">{invalidateMutation.error.message}</p>
              ) : null}
            </form>
          ) : (
            <p className="text-sm text-[var(--muted)]">Only ADMIN users can invalidate finalized snapshots.</p>
          )}
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <Card>
          <h3 className="mb-3 text-base font-semibold text-[var(--ink)]">Signals</h3>
          {signals.length === 0 ? (
            <p className="text-sm text-[var(--muted)]">No signals in payload.</p>
          ) : (
            <pre className="overflow-x-auto text-xs text-[var(--ink)]">{JSON.stringify(signals, null, 2)}</pre>
          )}
        </Card>
        <Card>
          <h3 className="mb-3 text-base font-semibold text-[var(--ink)]">Rule Results</h3>
          {ruleResults.length === 0 ? (
            <p className="text-sm text-[var(--muted)]">No rule results in payload.</p>
          ) : (
            <pre className="overflow-x-auto text-xs text-[var(--ink)]">{JSON.stringify(ruleResults, null, 2)}</pre>
          )}
        </Card>
        <Card>
          <h3 className="mb-3 text-base font-semibold text-[var(--ink)]">Contributing Signals</h3>
          {contributingSignals.length === 0 ? (
            <p className="text-sm text-[var(--muted)]">No contributing signals in payload.</p>
          ) : (
            <pre className="overflow-x-auto text-xs text-[var(--ink)]">{JSON.stringify(contributingSignals, null, 2)}</pre>
          )}
        </Card>
      </section>
    </div>
  );
}
