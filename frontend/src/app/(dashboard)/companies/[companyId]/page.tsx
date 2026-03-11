import { TopBar } from "@/components/layout/top-bar";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";

interface CompanyDetailPageProps {
  params: Promise<{ companyId: string }>;
}

export default async function CompanyDetailPage({ params }: CompanyDetailPageProps) {
  const { companyId } = await params;

  return (
    <div>
      <TopBar title="Company Intelligence" subtitle={`Company ID: ${companyId}`} />
      <main className="p-4 md:p-8">
        <Card>
          <CardTitle>Intelligence View Scaffolding</CardTitle>
          <CardDescription>
            Timeline and trends endpoints already exist. Full page activation depends on missing company detail and snapshots list endpoints.
          </CardDescription>
        </Card>
      </main>
    </div>
  );
}
