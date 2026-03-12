import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { fetchCompanyTimeline, fetchCompanyTrends } from "@/lib/api/analytics";
import { ApiError } from "@/lib/api/errors";
import { CompanySummaryDto } from "@/lib/api/types";

const ACCESS_COOKIE = "munqith_access_token";

function getConfiguredCompanies(): Array<{ id: string; name: string }> {
  const ids = (process.env.NEXT_PUBLIC_DEMO_COMPANY_IDS ?? process.env.NEXT_PUBLIC_DEMO_COMPANY_ID ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  const names = (process.env.NEXT_PUBLIC_DEMO_COMPANY_NAMES ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  return ids.map((id, index) => ({
    id,
    name: names[index] || `Company ${index + 1}`,
  }));
}

export async function GET() {
  const configuredCompanies = getConfiguredCompanies();
  if (configuredCompanies.length === 0) {
    return NextResponse.json([], { status: 200 });
  }

  const cookieStore = await cookies();
  const token = cookieStore.get(ACCESS_COOKIE)?.value;

  if (!token) {
    return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  }

  try {
    const summaries = await Promise.all(
      configuredCompanies.map(async (company) => {
        const [timelineResponse, trendsResponse] = await Promise.all([
          fetchCompanyTimeline(company.id, token),
          fetchCompanyTrends(company.id, token),
        ]);

        const latestTimeline = timelineResponse.timeline[timelineResponse.timeline.length - 1] ?? null;

        const summary: CompanySummaryDto = {
          id: company.id,
          name: company.name,
          latestStage: latestTimeline?.stage ?? null,
          latestSnapshotDate: latestTimeline?.snapshot_date ?? null,
          snapshotCount: trendsResponse.snapshot_count,
          revenueTrend: trendsResponse.indicators?.revenue_trend ?? null,
          burnTrend: trendsResponse.indicators?.burn_trend ?? null,
          runwayTrend: trendsResponse.indicators?.runway_trend ?? null,
        };

        return summary;
      }),
    );

    return NextResponse.json(summaries, { status: 200 });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ message: error.message }, { status: error.status || 500 });
    }

    return NextResponse.json({ message: "Failed to load companies" }, { status: 500 });
  }
}
