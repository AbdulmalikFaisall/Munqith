"use client";

import { AlertTriangle } from "lucide-react";

import { Button } from "@/components/ui/button";

interface ErrorStateProps {
  title: string;
  description: string;
  onRetry?: () => void;
}

export function ErrorState({ title, description, onRetry }: ErrorStateProps) {
  return (
    <div className="rounded-xl border border-rose-200 bg-rose-50 p-6">
      <div className="mb-3 flex items-center gap-2 text-rose-700">
        <AlertTriangle className="h-5 w-5" />
        <h3 className="font-semibold">{title}</h3>
      </div>
      <p className="mb-4 text-sm text-rose-800">{description}</p>
      {onRetry ? (
        <Button variant="outline" onClick={onRetry}>
          Retry
        </Button>
      ) : null}
    </div>
  );
}
