"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { StageBadge } from "@/components/intelligence/stage-badge";
import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { SkeletonCard } from "@/components/states/skeleton-card";
import { Card } from "@/components/ui/card";
import { useCompaniesQuery } from "@/features/companies/hooks/use-companies-query";

export function CompaniesTable() {
  const companiesQuery = useCompaniesQuery();
  const [searchTerm, setSearchTerm] = useState("");

  const filtered = useMemo(() => {
    const normalized = searchTerm.trim().toLowerCase();
    if (!normalized) {
      return companiesQuery.data ?? [];
    }

    return (companiesQuery.data ?? []).filter((company) => {
      return (
        company.name.toLowerCase().includes(normalized) ||
        company.id.toLowerCase().includes(normalized) ||
        (company.latestStage ?? "").toLowerCase().includes(normalized)
      );
    });
  }, [companiesQuery.data, searchTerm]);

  if (companiesQuery.isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
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

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <input
          type="search"
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
          placeholder="Search by company name, id, or stage"
          className="h-10 w-full rounded-md border border-[var(--line)] bg-white px-3 text-sm outline-none ring-[var(--brand)] focus:ring-2"
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          title="No companies available"
          description="Configure NEXT_PUBLIC_DEMO_COMPANY_IDS to populate the companies page until company list endpoint is released."
        />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((company) => (
            <Card key={company.id} className="space-y-3">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-semibold text-[var(--ink)]">{company.name}</p>
                <StageBadge stage={company.latestStage} />
              </div>

              <p className="text-xs text-[var(--muted)] break-all">{company.id}</p>
              <p className="text-sm text-[var(--muted)]">
                Latest Snapshot: {company.latestSnapshotDate ?? "N/A"} | Finalized Count: {company.snapshotCount}
              </p>

              <p className="text-xs text-[var(--muted)]">
                Revenue: {company.revenueTrend ?? "N/A"} | Burn: {company.burnTrend ?? "N/A"} | Runway: {company.runwayTrend ?? "N/A"}
              </p>

              <Link
                href={`/companies/${company.id}`}
                className="inline-flex h-9 items-center rounded-md bg-[var(--brand)] px-3 text-sm font-medium text-white"
              >
                Open Intelligence
              </Link>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
