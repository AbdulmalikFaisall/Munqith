import { TimelineItemDto } from "@/lib/api/types";

import { StageBadge } from "@/components/intelligence/stage-badge";

interface TimelineListProps {
  items: TimelineItemDto[];
}

export function TimelineList({ items }: TimelineListProps) {
  return (
    <div className="rounded-xl border border-[var(--line)] bg-white p-5">
      <h3 className="mb-4 text-base font-semibold text-[var(--ink)]">Timeline</h3>
      <ul className="space-y-3">
        {items.map((item) => (
          <li key={item.snapshot_date} className="rounded-lg border border-[var(--line)] p-3">
            <div className="mb-2 flex items-center justify-between gap-2">
              <p className="text-sm font-semibold text-[var(--ink)]">{item.snapshot_date}</p>
              <StageBadge stage={item.stage} />
            </div>
            <p className="text-xs text-[var(--muted)]">
              Revenue: {item.monthly_revenue.toLocaleString()} | Burn: {item.monthly_burn.toLocaleString()} | Runway: {item.runway_months.toFixed(2)}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
