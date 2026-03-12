import { TopBar } from "@/components/layout/top-bar";
import { CompanyIntelligenceView } from "@/features/companies/components/company-intelligence-view";

interface CompanyDetailPageProps {
  params: Promise<{ companyId: string }>;
}

export default async function CompanyDetailPage({ params }: CompanyDetailPageProps) {
  const { companyId } = await params;

  return (
    <div>
      <TopBar title="Company Intelligence" subtitle={`Company ID: ${companyId}`} />
      <main className="p-4 md:p-8">
        <CompanyIntelligenceView companyId={companyId} />
      </main>
    </div>
  );
}
