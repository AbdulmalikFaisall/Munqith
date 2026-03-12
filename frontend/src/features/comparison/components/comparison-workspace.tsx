"use client";

import { useMemo, useState } from "react";

import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { SkeletonCard } from "@/components/states/skeleton-card";
import { Card } from "@/components/ui/card";
import { useCompanyCompareQuery } from "@/features/companies/hooks/use-company-compare-query";
import { useCompanyIntelligenceQuery } from "@/features/companies/hooks/use-company-intelligence-query";
import { useCompaniesQuery } from "@/features/companies/hooks/use-companies-query";

function numberText(value: number | null | undefined, suffix = ""): string {
  if (value === null || value === undefined) {
    return "N/A";
  }
  return `${value.toLocaleString()}${suffix}`;
}

function deltaClass(value: number | null): string {
  if (value === null) {
    return "text-[var(--muted)]";
  }
  if (value > 0) {
    return "text-emerald-700";
  }
  if (value < 0) {
    return "text-rose-700";
  }
  return "text-[var(--ink)]";
}

export function ComparisonWorkspace() {
  const companiesQuery = useCompaniesQuery();
  const [selectedCompanyId, setSelectedCompanyId] = useState("");
  const effectiveCompanyId = selectedCompanyId || companiesQuery.data?.[0]?.id || "";

  const intelligenceQuery = useCompanyIntelligenceQuery(effectiveCompanyId);
  const dateOptions = useMemo(
    () => (intelligenceQuery.data?.timeline ?? []).map((item) => item.snapshot_date),
    [intelligenceQuery.data],
  );

  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  const hasInvalidDateOrder = Boolean(fromDate && toDate && fromDate > toDate);
  const compareQuery = useCompanyCompareQuery(
    effectiveCompanyId,
    hasInvalidDateOrder ? "" : fromDate,
    hasInvalidDateOrder ? "" : toDate,
  );

  if (companiesQuery.isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (companiesQuery.isError) {
    return (
      <ErrorState
        title="Unable to load companies"
        description={companiesQuery.error.message}
        onRetry={() => companiesQuery.refetch()}
      />
    );
  }

  if (!companiesQuery.data || companiesQuery.data.length === 0) {
    return <EmptyState title="No companies available" description="Create at least one company to run snapshot comparisons." />;
  }

  return (
    <div className="space-y-6">
      <Card className="space-y-4">
        <h3 className="text-base font-semibold text-[var(--ink)]">Comparison Controls</h3>
        <div className="grid gap-3 md:grid-cols-3">
          <select
            value={effectiveCompanyId}
            onChange={(event) => {
              setSelectedCompanyId(event.target.value);
              setFromDate("");
              setToDate("");
            }}
            className="h-10 rounded-md border border-[var(--line)] bg-white px-3 text-sm"
          >
            {companiesQuery.data.map((company) => (
              <option key={company.id} value={company.id}>
                {company.name}
              </option>
            ))}
          </select>

          <select
            value={fromDate}
            onChange={(event) => setFromDate(event.target.value)}
            className="h-10 rounded-md border border-[var(--line)] bg-white px-3 text-sm"
            disabled={!effectiveCompanyId || intelligenceQuery.isLoading}
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
            disabled={!effectiveCompanyId || intelligenceQuery.isLoading}
          >
            <option value="">To date</option>
            {dateOptions.map((date) => (
              <option key={`to-${date}`} value={date}>
                {date}
              </option>
            ))}
          </select>
        </div>
        <p className="text-sm text-[var(--muted)]">Pick two finalized dates for the same company to compute stage and metric deltas.</p>
      </Card>

      {!fromDate || !toDate ? (
        <EmptyState title="Select two dates" description="Comparison will run when both dates are selected." />
      ) : hasInvalidDateOrder ? (
        <ErrorState
          title="Invalid date range"
          description="From date must be earlier than or equal to To date."
          onRetry={() => {
            setFromDate("");
            setToDate("");
          }}
        />
      ) : compareQuery.isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : compareQuery.isError ? (
        <ErrorState
          title="Comparison unavailable"
          description={compareQuery.error.message}
          onRetry={() => compareQuery.refetch()}
        />
      ) : compareQuery.data ? (
        <>
          <section className="rounded-xl border border-[var(--line)] bg-white p-4">
            <p className="text-xs uppercase tracking-wide text-[var(--muted)]">Stage Transition</p>
            <p className="mt-1 text-lg font-semibold text-[var(--ink)]">
              {compareQuery.data.from_stage ?? "N/A"} → {compareQuery.data.to_stage ?? "N/A"}
            </p>
            <p className="text-sm text-[var(--muted)]">
              {compareQuery.data.stage_changed ? "Stage changed between selected snapshots." : "No stage change between selected snapshots."}
            </p>
          </section>

          <section className="grid gap-4 md:grid-cols-2">
            <Card className="space-y-2">
              <p className="text-sm font-semibold text-[var(--ink)]">From ({compareQuery.data.from_date})</p>
              <p className="text-sm text-[var(--muted)]">Revenue: {numberText(compareQuery.data.from_metrics.monthly_revenue)}</p>
              <p className="text-sm text-[var(--muted)]">Burn: {numberText(compareQuery.data.from_metrics.monthly_burn)}</p>
              <p className="text-sm text-[var(--muted)]">Runway: {numberText(compareQuery.data.from_metrics.runway_months, " months")}</p>
            </Card>
            <Card className="space-y-2">
              <p className="text-sm font-semibold text-[var(--ink)]">To ({compareQuery.data.to_date})</p>
              <p className="text-sm text-[var(--muted)]">Revenue: {numberText(compareQuery.data.to_metrics.monthly_revenue)}</p>
              <p className="text-sm text-[var(--muted)]">Burn: {numberText(compareQuery.data.to_metrics.monthly_burn)}</p>
              <p className="text-sm text-[var(--muted)]">Runway: {numberText(compareQuery.data.to_metrics.runway_months, " months")}</p>
            </Card>
          </section>

          <section className="grid gap-4 md:grid-cols-3">
            <Card>
              <p className="text-xs uppercase tracking-wide text-[var(--muted)]">Revenue Delta</p>
              <p className={`mt-2 text-2xl font-semibold ${deltaClass(compareQuery.data.deltas.delta_revenue)}`}>
                {numberText(compareQuery.data.deltas.delta_revenue)}
              </p>
            </Card>
            <Card>
              <p className="text-xs uppercase tracking-wide text-[var(--muted)]">Burn Delta</p>
              <p className={`mt-2 text-2xl font-semibold ${deltaClass(compareQuery.data.deltas.delta_burn)}`}>
                {numberText(compareQuery.data.deltas.delta_burn)}
              </p>
            </Card>
            <Card>
              <p className="text-xs uppercase tracking-wide text-[var(--muted)]">Runway Delta</p>
              <p className={`mt-2 text-2xl font-semibold ${deltaClass(compareQuery.data.deltas.delta_runway)}`}>
                {numberText(compareQuery.data.deltas.delta_runway, " months")}
              </p>
            </Card>
          </section>
        </>
      ) : null}
    </div>
  );
}
