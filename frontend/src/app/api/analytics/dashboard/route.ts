import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { fetchCompanyTimeline, fetchCompanyTrends } from "@/lib/api/analytics";
import { ApiError } from "@/lib/api/errors";
import { DashboardSummaryDto, TimelineItemDto } from "@/lib/api/types";

const ACCESS_COOKIE = "munqith_access_token";

function countTransitions(items: TimelineItemDto[]): number {
  return items.filter((item) => Boolean(item.stage_transition_from_previous)).length;
}

export async function GET(request: NextRequest) {
  const companyId = request.nextUrl.searchParams.get("companyId")?.trim();

  if (!companyId) {
    return NextResponse.json({ message: "companyId query parameter is required" }, { status: 400 });
  }

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

    const latestTimeline = timelineResponse.timeline[timelineResponse.timeline.length - 1] ?? null;
    const latestTrend = trendsResponse.time_series[trendsResponse.time_series.length - 1] ?? null;

    const summary: DashboardSummaryDto = {
      companyId,
      latestStage: latestTimeline?.stage ?? null,
      latestRunwayMonths: latestTrend?.runway_months ?? null,
      latestMonthlyBurn: latestTrend?.monthly_burn ?? null,
      latestMonthlyRevenue: latestTrend?.monthly_revenue ?? null,
      snapshotCount: trendsResponse.snapshot_count,
      transitionsCount: countTransitions(timelineResponse.timeline),
      indicators: trendsResponse.indicators,
      timeline: timelineResponse.timeline,
      trends: trendsResponse.time_series,
    };

    return NextResponse.json(summary, { status: 200 });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ message: error.message }, { status: error.status || 500 });
    }

    return NextResponse.json({ message: "Dashboard fetch failed" }, { status: 500 });
  }
}
