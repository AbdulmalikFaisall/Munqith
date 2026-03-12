"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { SkeletonCard } from "@/components/states/skeleton-card";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useCompaniesQuery } from "@/features/companies/hooks/use-companies-query";
import { useCreateSnapshotMutation } from "@/features/snapshots/hooks/use-snapshot-actions";

export function CreateSnapshotForm() {
  const router = useRouter();
  const companiesQuery = useCompaniesQuery();
  const createMutation = useCreateSnapshotMutation();

  const [companyId, setCompanyId] = useState("");
  const [snapshotDate, setSnapshotDate] = useState("");
  const [cashBalance, setCashBalance] = useState("");
  const [monthlyRevenue, setMonthlyRevenue] = useState("");
  const [operatingCosts, setOperatingCosts] = useState("");
  const effectiveCompanyId = companyId || companiesQuery.data?.[0]?.id || "";

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const response = await createMutation.mutateAsync({
      company_id: effectiveCompanyId,
      snapshot_date: snapshotDate,
      cash_balance: cashBalance ? Number(cashBalance) : undefined,
      monthly_revenue: monthlyRevenue ? Number(monthlyRevenue) : undefined,
      operating_costs: operatingCosts ? Number(operatingCosts) : undefined,
    });

    router.push(`/snapshots/${response.id}`);
  }

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
    return (
      <EmptyState
        title="No companies available"
        description="Create a company first, then return here to create snapshots."
      />
    );
  }

  return (
    <Card className="space-y-4">
      <h3 className="text-base font-semibold text-[var(--ink)]">Create DRAFT Snapshot</h3>
      <form className="space-y-4" onSubmit={onSubmit}>
        <div className="grid gap-4 md:grid-cols-2">
          <label className="space-y-1 text-sm text-[var(--ink)]">
            <span>Company</span>
            <select
              required
              value={effectiveCompanyId}
              onChange={(event) => setCompanyId(event.target.value)}
              className="h-10 w-full rounded-md border border-[var(--line)] bg-white px-3 text-sm"
            >
              {companiesQuery.data.map((company) => (
                <option key={company.id} value={company.id}>
                  {company.name}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-1 text-sm text-[var(--ink)]">
            <span>Snapshot Date</span>
            <input
              required
              type="date"
              value={snapshotDate}
              onChange={(event) => setSnapshotDate(event.target.value)}
              className="h-10 w-full rounded-md border border-[var(--line)] bg-white px-3 text-sm"
            />
          </label>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <label className="space-y-1 text-sm text-[var(--ink)]">
            <span>Cash Balance</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={cashBalance}
              onChange={(event) => setCashBalance(event.target.value)}
              placeholder="Optional"
              className="h-10 w-full rounded-md border border-[var(--line)] bg-white px-3 text-sm"
            />
          </label>

          <label className="space-y-1 text-sm text-[var(--ink)]">
            <span>Monthly Revenue</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={monthlyRevenue}
              onChange={(event) => setMonthlyRevenue(event.target.value)}
              placeholder="Optional"
              className="h-10 w-full rounded-md border border-[var(--line)] bg-white px-3 text-sm"
            />
          </label>

          <label className="space-y-1 text-sm text-[var(--ink)]">
            <span>Operating Costs</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={operatingCosts}
              onChange={(event) => setOperatingCosts(event.target.value)}
              placeholder="Optional"
              className="h-10 w-full rounded-md border border-[var(--line)] bg-white px-3 text-sm"
            />
          </label>
        </div>

        <Button type="submit" disabled={createMutation.isPending}>
          {createMutation.isPending ? "Creating..." : "Create Snapshot"}
        </Button>

        {createMutation.error ? <p className="text-sm text-rose-700">{createMutation.error.message}</p> : null}
      </form>
    </Card>
  );
}
