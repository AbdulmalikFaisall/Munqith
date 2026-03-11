import { TopBar } from "@/components/layout/top-bar";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";

export default function CompaniesPage() {
  return (
    <div>
      <TopBar title="Companies" subtitle="Portfolio intelligence entries and stage visibility" />
      <main className="p-4 md:p-8">
        <Card>
          <CardTitle>Companies API Pending</CardTitle>
          <CardDescription>
            This page is scaffolded in Phase 2. Full data view depends on missing backend endpoints: GET /companies and GET /companies/{'{id}'}.
          </CardDescription>
        </Card>
      </main>
    </div>
  );
}
