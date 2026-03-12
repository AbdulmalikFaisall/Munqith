import { TopBar } from "@/components/layout/top-bar";
import { SnapshotDetailView } from "@/features/snapshots/components/snapshot-detail-view";

interface SnapshotDetailPageProps {
  params: Promise<{ snapshotId: string }>;
}

export default async function SnapshotDetailPage({ params }: SnapshotDetailPageProps) {
  const { snapshotId } = await params;

  return (
    <div>
      <TopBar title="Snapshot Details" subtitle={`Snapshot ID: ${snapshotId}`} />
      <main className="p-4 md:p-8">
        <SnapshotDetailView snapshotId={snapshotId} />
      </main>
    </div>
  );
}
