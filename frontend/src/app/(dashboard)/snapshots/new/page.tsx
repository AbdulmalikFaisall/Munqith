import { TopBar } from "@/components/layout/top-bar";
import { CreateSnapshotForm } from "@/features/snapshots/components/create-snapshot-form";

export default function CreateSnapshotPage() {
  return (
    <div>
      <TopBar title="Create Snapshot" subtitle="Start lifecycle with a DRAFT snapshot" />
      <main className="p-4 md:p-8">
        <CreateSnapshotForm />
      </main>
    </div>
  );
}
