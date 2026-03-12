import { TopBar } from "@/components/layout/top-bar";
import { ComparisonWorkspace } from "@/features/comparison/components/comparison-workspace";

export default function ComparisonPage() {
  return (
    <div>
      <TopBar title="Snapshot Comparison" subtitle="Compare finalized points in time for one company" />
      <main className="p-4 md:p-8">
        <ComparisonWorkspace />
      </main>
    </div>
  );
}
