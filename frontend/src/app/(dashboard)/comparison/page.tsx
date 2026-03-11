import { TopBar } from "@/components/layout/top-bar";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";

export default function ComparisonPage() {
  return (
    <div>
      <TopBar title="Snapshot Comparison" subtitle="Compare finalized points in time for one company" />
      <main className="p-4 md:p-8">
        <Card>
          <CardTitle>Comparison Workspace</CardTitle>
          <CardDescription>
            Route shell is ready. Phase 3+ will connect query hooks to /api/v1/companies/{'{company_id}'}/snapshots/compare.
          </CardDescription>
        </Card>
      </main>
    </div>
  );
}
