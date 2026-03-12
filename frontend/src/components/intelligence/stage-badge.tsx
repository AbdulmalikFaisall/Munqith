import { cn } from "@/lib/utils";

interface StageBadgeProps {
  stage: string | null;
}

const STAGE_COLORS: Record<string, string> = {
  IDEA: "bg-zinc-100 text-zinc-700",
  PRE_SEED: "bg-sky-100 text-sky-700",
  SEED: "bg-emerald-100 text-emerald-700",
  SERIES_A: "bg-amber-100 text-amber-700",
  GROWTH: "bg-violet-100 text-violet-700",
};

export function StageBadge({ stage }: StageBadgeProps) {
  const label = stage ?? "UNKNOWN";
  return (
    <span
      className={cn(
        "inline-flex rounded-full px-2.5 py-1 text-xs font-semibold",
        STAGE_COLORS[label] ?? "bg-zinc-100 text-zinc-700",
      )}
    >
      {label}
    </span>
  );
}
