import { TopBar } from "@/components/layout/top-bar";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";

interface SnapshotDetailPageProps {
  params: Promise<{ snapshotId: string }>;
}

export default async function SnapshotDetailPage({ params }: SnapshotDetailPageProps) {
  const { snapshotId } = await params;

  return (
    <div>
      <TopBar title="Snapshot Details" subtitle={`Snapshot ID: ${snapshotId}`} />
      <main className="p-4 md:p-8">
        <Card>
          <CardTitle>Snapshot Detail Placeholder</CardTitle>
          <CardDescription>
            This page is structured in Phase 2. Full details require GET /snapshots/{'{id}'}, while export and invalidation endpoints are already available.
          </CardDescription>
        </Card>
      </main>
    </div>
  );
}
