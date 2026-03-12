import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { fetchCompanyComparison } from "@/lib/api/analytics";
import { ApiError } from "@/lib/api/errors";

const ACCESS_COOKIE = "munqith_access_token";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ companyId: string }> },
) {
  const { companyId } = await params;
  const fromDate = request.nextUrl.searchParams.get("fromDate")?.trim();
  const toDate = request.nextUrl.searchParams.get("toDate")?.trim();

  if (!fromDate || !toDate) {
    return NextResponse.json({ message: "fromDate and toDate are required" }, { status: 400 });
  }

  const cookieStore = await cookies();
  const token = cookieStore.get(ACCESS_COOKIE)?.value;

  if (!token) {
    return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  }

  try {
    const comparison = await fetchCompanyComparison(companyId, fromDate, toDate, token);
    return NextResponse.json(comparison, { status: 200 });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ message: error.message }, { status: error.status || 500 });
    }

    return NextResponse.json({ message: "Failed to compare snapshots" }, { status: 500 });
  }
}
