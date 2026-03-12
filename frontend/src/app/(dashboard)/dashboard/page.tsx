import { cookies } from "next/headers";

import { TopBar } from "@/components/layout/top-bar";
import { DashboardOverview } from "@/features/dashboard/components/dashboard-overview";

export default async function DashboardPage() {
  const cookieStore = await cookies();
  const fallbackCompanyId = process.env.NEXT_PUBLIC_DEMO_COMPANY_ID ?? "";
  const selectedCompanyId = cookieStore.get("munqith_selected_company")?.value ?? fallbackCompanyId;

  return (
    <div>
      <TopBar
        title="Executive Dashboard"
        subtitle="Current state, explainability, and momentum across portfolio companies"
      />
      <DashboardOverview companyId={selectedCompanyId} />
    </div>
  );
}
