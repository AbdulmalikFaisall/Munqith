"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { TrendLineChart } from "@/components/charts/trend-line-chart";
import { MetricCard } from "@/components/intelligence/metric-card";
import { StageBadge } from "@/components/intelligence/stage-badge";
import { TimelineList } from "@/components/intelligence/timeline-list";
import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { SkeletonCard } from "@/components/states/skeleton-card";
import { Card } from "@/components/ui/card";
import { useCompanyCompareQuery } from "@/features/companies/hooks/use-company-compare-query";
import { useCompanyIntelligenceQuery } from "@/features/companies/hooks/use-company-intelligence-query";

interface CompanyIntelligenceViewProps {
  companyId: string;
}

export function CompanyIntelligenceView({ companyId }: CompanyIntelligenceViewProps) {
  const intelligenceQuery = useCompanyIntelligenceQuery(companyId);

  const dateOptions = useMemo(() => {
    return (intelligenceQuery.data?.timeline ?? []).map((item) => item.snapshot_date);
  }, [intelligenceQuery.data]);

  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const compareQuery = useCompanyCompareQuery(companyId, fromDate, toDate);

  if (intelligenceQuery.isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (intelligenceQuery.isError) {
    return (
      <ErrorState
        title="Unable to load company intelligence"
        description={intelligenceQuery.error.message}
        onRetry={() => intelligenceQuery.refetch()}
      />
    );
  }

  const data = intelligenceQuery.data;
  if (!data || data.timeline.length === 0) {
    return (
      <EmptyState
        title="No finalized intelligence"
        description="This company has no finalized snapshots available in timeline and trends endpoints."
      />
    );
  }

  const latest = data.timeline[data.timeline.length - 1];

  return (
    <div className="space-y-6">
      <section className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[var(--line)] bg-white p-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-[var(--muted)]">Current State</p>
          <p className="mt-1 text-lg font-semibold text-[var(--ink)]">{data.companyName}</p>
          <p className="text-sm text-[var(--muted)]">Company ID: {data.companyId}</p>
        </div>
        <StageBadge stage={data.latestStage} />
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Latest Snapshot" value={latest.snapshot_date} />
        <MetricCard label="Runway" value={`${latest.runway_months.toFixed(2)} months`} />
        <MetricCard label="Monthly Burn" value={latest.monthly_burn.toLocaleString()} />
        <MetricCard label="Monthly Revenue" value={latest.monthly_revenue.toLocaleString()} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[2fr_1fr]">
        <TrendLineChart points={data.trends} />
        <TimelineList items={data.timeline.slice().reverse()} />
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <Card className="space-y-3">
          <h3 className="text-base font-semibold text-[var(--ink)]">Snapshot Comparison</h3>
          <div className="grid gap-3 md:grid-cols-2">
            <select
              value={fromDate}
              onChange={(event) => setFromDate(event.target.value)}
              className="h-10 rounded-md border border-[var(--line)] bg-white px-3 text-sm"
            >
              <option value="">From date</option>
              {dateOptions.map((date) => (
                <option key={`from-${date}`} value={date}>
                  {date}
                </option>
              ))}
            </select>
            <select
              value={toDate}
              onChange={(event) => setToDate(event.target.value)}
              className="h-10 rounded-md border border-[var(--line)] bg-white px-3 text-sm"
            >
              <option value="">To date</option>
              {dateOptions.map((date) => (
                <option key={`to-${date}`} value={date}>
                  {date}
                </option>
              ))}
            </select>
          </div>

          {!fromDate || !toDate ? (
            <p className="text-sm text-[var(--muted)]">Choose two finalized dates to run comparison.</p>
          ) : compareQuery.isError ? (
            <p className="text-sm text-rose-700">{compareQuery.error.message}</p>
          ) : compareQuery.isLoading ? (
            <p className="text-sm text-[var(--muted)]">Computing comparison...</p>
          ) : compareQuery.data ? (
            <div className="space-y-2 text-sm text-[var(--ink)]">
              <p>
                Stage: {compareQuery.data.from_stage} → {compareQuery.data.to_stage}
              </p>
              <p>Revenue Delta: {compareQuery.data.deltas.delta_revenue.toLocaleString()}</p>
              <p>Burn Delta: {compareQuery.data.deltas.delta_burn.toLocaleString()}</p>
              <p>Runway Delta: {compareQuery.data.deltas.delta_runway.toFixed(2)}</p>
            </div>
          ) : null}
        </Card>

        <Card className="space-y-3">
          <h3 className="text-base font-semibold text-[var(--ink)]">Snapshot Details Access</h3>
          <p className="text-sm text-[var(--muted)]">
            Backend currently does not expose snapshot ids in timeline/trends. Use known finalized snapshot IDs from operations logs to open detail pages.
          </p>
          <div className="space-y-2 text-sm">
            <p>Open manually: /snapshots/{'{snapshotId}'}</p>
            <p className="text-[var(--muted)]">
              Detail page is fully wired through export JSON, export PDF, and invalidation endpoints.
            </p>
          </div>
          <Link href="/comparison" className="inline-flex h-9 items-center rounded-md border border-[var(--line)] px-3 text-sm">
            Open Comparison Workspace
          </Link>
        </Card>
      </section>
    </div>
  );
}
