import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { fetchCompanyTimeline, fetchCompanyTrends } from "@/lib/api/analytics";
import { ApiError } from "@/lib/api/errors";
import { CompanyIntelligenceDto, CompanySnapshotItemDto } from "@/lib/api/types";

const ACCESS_COOKIE = "munqith_access_token";

function companyNameFromId(companyId: string): string {
  const ids = (process.env.NEXT_PUBLIC_DEMO_COMPANY_IDS ?? process.env.NEXT_PUBLIC_DEMO_COMPANY_ID ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
  const names = (process.env.NEXT_PUBLIC_DEMO_COMPANY_NAMES ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  const foundIndex = ids.findIndex((id) => id === companyId);
  if (foundIndex >= 0) {
    return names[foundIndex] || `Company ${foundIndex + 1}`;
  }

  return companyId;
}

export async function GET(_request: Request, { params }: { params: Promise<{ companyId: string }> }) {
  const { companyId } = await params;
  const cookieStore = await cookies();
  const token = cookieStore.get(ACCESS_COOKIE)?.value;

  if (!token) {
    return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  }

  try {
    const [timelineResponse, trendsResponse] = await Promise.all([
      fetchCompanyTimeline(companyId, token),
      fetchCompanyTrends(companyId, token),
    ]);

    const snapshots: CompanySnapshotItemDto[] = timelineResponse.timeline.map((item) => ({
      id: null,
      snapshot_date: item.snapshot_date,
      stage: item.stage,
      monthly_revenue: item.monthly_revenue,
      monthly_burn: item.monthly_burn,
      runway_months: item.runway_months,
      status: "FINALIZED",
    }));

    const latest = timelineResponse.timeline[timelineResponse.timeline.length - 1] ?? null;

    const response: CompanyIntelligenceDto = {
      companyId,
      companyName: companyNameFromId(companyId),
      latestStage: latest?.stage ?? null,
      timeline: timelineResponse.timeline,
      trends: trendsResponse.time_series,
      indicators: trendsResponse.indicators,
      snapshots,
    };

    return NextResponse.json(response, { status: 200 });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ message: error.message }, { status: error.status || 500 });
    }

    return NextResponse.json({ message: "Failed to load company intelligence" }, { status: 500 });
  }
}
