import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { ApiError } from "@/lib/api/errors";
import { fetchSnapshotDetail } from "@/lib/api/snapshots";

const ACCESS_COOKIE = "munqith_access_token";

export async function GET(_request: Request, { params }: { params: Promise<{ snapshotId: string }> }) {
  const { snapshotId } = await params;
  const cookieStore = await cookies();
  const token = cookieStore.get(ACCESS_COOKIE)?.value;

  if (!token) {
    return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  }

  try {
    const detail = await fetchSnapshotDetail(snapshotId, token);
    return NextResponse.json(detail, { status: 200 });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ message: error.message }, { status: error.status || 500 });
    }

    return NextResponse.json({ message: "Failed to load snapshot detail" }, { status: 500 });
  }
}
