import { TopBar } from "@/components/layout/top-bar";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";

export default function DashboardPage() {
  return (
    <div>
      <TopBar
        title="Executive Dashboard"
        subtitle="Current state, explainability, and momentum across portfolio companies"
      />

      <main className="grid gap-4 p-4 md:grid-cols-2 md:gap-6 md:p-8 xl:grid-cols-4">
        <Card>
          <CardDescription>Current Focus</CardDescription>
          <CardTitle>Backend Dependency Alignment</CardTitle>
        </Card>
        <Card>
          <CardDescription>Signal</CardDescription>
          <CardTitle>Phase 2 Shell Ready</CardTitle>
        </Card>
        <Card>
          <CardDescription>Next Phase</CardDescription>
          <CardTitle>API Client + Auth Wiring</CardTitle>
        </Card>
        <Card>
          <CardDescription>Guardrail</CardDescription>
          <CardTitle>No Frontend Business Logic</CardTitle>
        </Card>
      </main>
    </div>
  );
}
