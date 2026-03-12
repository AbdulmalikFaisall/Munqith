import { CircleDashed } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description: string;
}

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="rounded-xl border border-dashed border-[var(--line)] bg-white p-8 text-center">
      <CircleDashed className="mx-auto mb-3 h-6 w-6 text-[var(--muted)]" />
      <h3 className="text-base font-semibold text-[var(--ink)]">{title}</h3>
      <p className="mt-1 text-sm text-[var(--muted)]">{description}</p>
    </div>
  );
}
