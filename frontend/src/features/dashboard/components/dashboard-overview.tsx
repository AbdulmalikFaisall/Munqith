"use client";

import { TrendLineChart } from "@/components/charts/trend-line-chart";
import { MetricCard } from "@/components/intelligence/metric-card";
import { StageBadge } from "@/components/intelligence/stage-badge";
import { TimelineList } from "@/components/intelligence/timeline-list";
import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { SkeletonCard } from "@/components/states/skeleton-card";
import { useDashboardQuery } from "@/features/dashboard/hooks/use-dashboard-query";

interface DashboardOverviewProps {
  companyId: string;
}

export function DashboardOverview({ companyId }: DashboardOverviewProps) {
  const dashboardQuery = useDashboardQuery(companyId);

  if (!companyId) {
    return (
      <main className="p-4 md:p-8">
        <EmptyState
          title="No company selected"
          description="Select or create a company, then return to dashboard insights."
        />
      </main>
    );
  }

  const formatted = dashboardQuery.data
    ? {
        ...dashboardQuery.data,
        runwayLabel:
          dashboardQuery.data.latestRunwayMonths !== null
            ? `${dashboardQuery.data.latestRunwayMonths.toFixed(2)} months`
            : "N/A",
        burnLabel:
          dashboardQuery.data.latestMonthlyBurn !== null
            ? dashboardQuery.data.latestMonthlyBurn.toLocaleString()
            : "N/A",
        revenueLabel:
          dashboardQuery.data.latestMonthlyRevenue !== null
            ? dashboardQuery.data.latestMonthlyRevenue.toLocaleString()
            : "N/A",
      }
    : null;

  if (dashboardQuery.isLoading) {
    return (
      <div className="grid gap-4 p-4 md:grid-cols-2 md:gap-6 md:p-8 xl:grid-cols-4">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (dashboardQuery.isError) {
    return (
      <main className="p-4 md:p-8">
        <ErrorState
          title="Dashboard data unavailable"
          description={dashboardQuery.error.message}
          onRetry={() => dashboardQuery.refetch()}
        />
      </main>
    );
  }

  if (!formatted || formatted.snapshotCount === 0) {
    return (
      <main className="p-4 md:p-8">
        <EmptyState
          title="No finalized snapshots found"
          description="Create and finalize snapshots to unlock trend and stage intelligence."
        />
      </main>
    );
  }

  return (
    <main className="space-y-6 p-4 md:p-8">
      <section className="flex items-center gap-3">
        <p className="text-sm text-[var(--muted)]">Current stage:</p>
        <StageBadge stage={formatted.latestStage} />
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Runway" value={formatted.runwayLabel} />
        <MetricCard label="Monthly Burn" value={formatted.burnLabel} />
        <MetricCard label="Monthly Revenue" value={formatted.revenueLabel} />
        <MetricCard label="Stage Transitions" value={String(formatted.transitionsCount)} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[2fr_1fr]">
        <TrendLineChart points={formatted.trends} />
        <TimelineList items={formatted.timeline.slice().reverse()} />
      </section>
    </main>
  );
}
