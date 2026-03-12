export function SkeletonCard() {
  return (
    <div className="animate-pulse rounded-xl border border-[var(--line)] bg-white p-5">
      <div className="h-3 w-28 rounded bg-[var(--surface-soft)]" />
      <div className="mt-4 h-7 w-32 rounded bg-[var(--surface-soft)]" />
      <div className="mt-3 h-3 w-44 rounded bg-[var(--surface-soft)]" />
    </div>
  );
}
