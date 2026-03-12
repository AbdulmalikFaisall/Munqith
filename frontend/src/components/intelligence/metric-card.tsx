import { Card, CardDescription, CardTitle } from "@/components/ui/card";

interface MetricCardProps {
  label: string;
  value: string;
  caption?: string;
}

export function MetricCard({ label, value, caption }: MetricCardProps) {
  return (
    <Card>
      <CardDescription>{label}</CardDescription>
      <CardTitle className="mt-2 text-2xl">{value}</CardTitle>
      {caption ? <p className="mt-2 text-xs text-[var(--muted)]">{caption}</p> : null}
    </Card>
  );
}
