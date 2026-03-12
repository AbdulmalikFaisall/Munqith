import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { fetchCompanyTimeline, fetchCompanyTrends } from "@/lib/api/analytics";
import { fetchCompanyDetail, fetchCompanySnapshots } from "@/lib/api/companies";
import { ApiError } from "@/lib/api/errors";
import { CompanyIntelligenceDto } from "@/lib/api/types";

const ACCESS_COOKIE = "munqith_access_token";

export async function GET(_request: Request, { params }: { params: Promise<{ companyId: string }> }) {
  const { companyId } = await params;
  const cookieStore = await cookies();
  const token = cookieStore.get(ACCESS_COOKIE)?.value;

  if (!token) {
    return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  }

  try {
    const [companyDetail, timelineResponse, trendsResponse, snapshotsResponse] = await Promise.all([
      fetchCompanyDetail(companyId, token),
      fetchCompanyTimeline(companyId, token),
      fetchCompanyTrends(companyId, token),
      fetchCompanySnapshots(companyId, token),
    ]);

    const latest = timelineResponse.timeline[timelineResponse.timeline.length - 1] ?? null;

    const response: CompanyIntelligenceDto = {
      companyId,
      companyName: companyDetail.name,
      companySector: companyDetail.sector,
      latestStage: latest?.stage ?? null,
      timeline: timelineResponse.timeline,
      trends: trendsResponse.time_series,
      indicators: trendsResponse.indicators,
      snapshots: snapshotsResponse.snapshots,
    };

    return NextResponse.json(response, { status: 200 });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ message: error.message }, { status: error.status || 500 });
    }

    return NextResponse.json({ message: "Failed to load company intelligence" }, { status: 500 });
  }
}
