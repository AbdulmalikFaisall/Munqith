import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { ApiError } from "@/lib/api/errors";
import { invalidateSnapshot } from "@/lib/api/snapshots";

const ACCESS_COOKIE = "munqith_access_token";

export async function POST(request: NextRequest, { params }: { params: Promise<{ snapshotId: string }> }) {
  const { snapshotId } = await params;
  const payload = (await request.json().catch(() => null)) as { reason?: string } | null;

  if (!payload?.reason?.trim()) {
    return NextResponse.json({ message: "reason is required" }, { status: 400 });
  }

  const cookieStore = await cookies();
  const token = cookieStore.get(ACCESS_COOKIE)?.value;

  if (!token) {
    return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  }

  try {
    const response = await invalidateSnapshot(snapshotId, { reason: payload.reason.trim() }, token);
    return NextResponse.json(response, { status: 200 });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ message: error.message }, { status: error.status || 500 });
    }

    return NextResponse.json({ message: "Failed to invalidate snapshot" }, { status: 500 });
  }
}
