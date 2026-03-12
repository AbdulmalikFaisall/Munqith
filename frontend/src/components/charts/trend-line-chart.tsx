"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface TrendPoint {
  date: string;
  monthly_revenue: number;
  monthly_burn: number;
  runway_months: number;
}

interface TrendLineChartProps {
  points: TrendPoint[];
}

export function TrendLineChart({ points }: TrendLineChartProps) {
  return (
    <div className="h-80 w-full rounded-xl border border-[var(--line)] bg-white p-3">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points} margin={{ top: 12, right: 8, bottom: 12, left: 8 }}>
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Line type="monotone" dataKey="monthly_revenue" stroke="#1e6091" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="monthly_burn" stroke="#ca6702" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="runway_months" stroke="#3a5a40" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
