"use client";

import { useMemo, useState } from "react";
import Link from "next/link";

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
  const metricText = (value: number | null, suffix = "") => {
    if (value === null) {
      return "N/A";
    }
    return `${value.toLocaleString()}${suffix}`;
  };
  const deltaText = (value: number | null, suffix = "") => {
    if (value === null) {
      return "N/A";
    }
    return `${value.toLocaleString()}${suffix}`;
  };

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
        <MetricCard label="Runway" value={metricText(latest.runway_months, " months")} />
        <MetricCard label="Monthly Burn" value={metricText(latest.monthly_burn)} />
        <MetricCard label="Monthly Revenue" value={metricText(latest.monthly_revenue)} />
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
                Stage: {compareQuery.data.from_stage ?? "N/A"} → {compareQuery.data.to_stage ?? "N/A"}
              </p>
              <p>Revenue Delta: {deltaText(compareQuery.data.deltas.delta_revenue)}</p>
              <p>Burn Delta: {deltaText(compareQuery.data.deltas.delta_burn)}</p>
              <p>Runway Delta: {deltaText(compareQuery.data.deltas.delta_runway, " months")}</p>
            </div>
          ) : null}
        </Card>

        <Card className="space-y-3">
          <h3 className="text-base font-semibold text-[var(--ink)]">Snapshots</h3>
          <div className="max-h-72 space-y-2 overflow-y-auto pr-1">
            {data.snapshots.length === 0 ? (
              <p className="text-sm text-[var(--muted)]">No snapshots available.</p>
            ) : (
              data.snapshots
                .slice()
                .reverse()
                .map((snapshot) => (
                  <div
                    key={snapshot.id}
                    className="flex items-center justify-between gap-3 rounded-md border border-[var(--line)] bg-[var(--surface-soft)] p-2"
                  >
                    <div>
                      <p className="text-sm font-medium text-[var(--ink)]">{snapshot.snapshot_date}</p>
                      <p className="text-xs text-[var(--muted)]">
                        {snapshot.status} | Stage: {snapshot.stage ?? "N/A"}
                      </p>
                    </div>
                    <Link
                      href={`/snapshots/${snapshot.id}`}
                      className="inline-flex h-8 items-center rounded-md border border-[var(--line)] px-3 text-xs font-medium"
                    >
                      Open
                    </Link>
                  </div>
                ))
            )}
          </div>
          <Link href="/comparison" className="inline-flex h-9 items-center rounded-md border border-[var(--line)] px-3 text-sm">
            Open Comparison Workspace
          </Link>
        </Card>
      </section>
    </div>
  );
}
