import { TopBar } from "@/components/layout/top-bar";
import { CompaniesTable } from "@/features/companies/components/companies-table";

export default function CompaniesPage() {
  return (
    <div>
      <TopBar title="Companies" subtitle="Portfolio intelligence entries and stage visibility" />
      <main className="p-4 md:p-8">
        <CompaniesTable />
      </main>
    </div>
  );
}
