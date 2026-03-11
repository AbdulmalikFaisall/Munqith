import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type DivProps = HTMLAttributes<HTMLDivElement>;

export function Card({ className, ...props }: DivProps) {
  return (
    <div
      className={cn(
        "rounded-xl border border-[var(--line)] bg-white p-5 shadow-[0_8px_30px_rgba(20,33,61,0.08)]",
        className,
      )}
      {...props}
    />
  );
}

export function CardTitle({ className, ...props }: DivProps) {
  return <h3 className={cn("text-base font-semibold text-[var(--ink)]", className)} {...props} />;
}

export function CardDescription({ className, ...props }: DivProps) {
  return <p className={cn("text-sm text-[var(--muted)]", className)} {...props} />;
}
