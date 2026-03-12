import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { ApiError } from "@/lib/api/errors";
import { createSnapshot } from "@/lib/api/snapshots";
import { CreateSnapshotRequestDto } from "@/lib/api/types";

const ACCESS_COOKIE = "munqith_access_token";

export async function POST(request: NextRequest) {
  const payload = (await request.json().catch(() => null)) as CreateSnapshotRequestDto | null;

  if (!payload?.company_id || !payload?.snapshot_date) {
    return NextResponse.json({ message: "company_id and snapshot_date are required" }, { status: 400 });
  }

  const cookieStore = await cookies();
  const token = cookieStore.get(ACCESS_COOKIE)?.value;

  if (!token) {
    return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  }

  try {
    const response = await createSnapshot(payload, token);
    return NextResponse.json(response, { status: 201 });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ message: error.message }, { status: error.status || 500 });
    }

    return NextResponse.json({ message: "Failed to create snapshot" }, { status: 500 });
  }
}
