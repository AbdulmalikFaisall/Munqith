import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { ApiError } from "@/lib/api/errors";
import { fetchSnapshotPdf } from "@/lib/api/snapshots";

const ACCESS_COOKIE = "munqith_access_token";

export async function GET(_request: Request, { params }: { params: Promise<{ snapshotId: string }> }) {
  const { snapshotId } = await params;
  const cookieStore = await cookies();
  const token = cookieStore.get(ACCESS_COOKIE)?.value;

  if (!token) {
    return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  }

  try {
    const response = await fetchSnapshotPdf(snapshotId, token);
    const arrayBuffer = await response.arrayBuffer();

    return new NextResponse(arrayBuffer, {
      status: 200,
      headers: {
        "Content-Type": response.headers.get("content-type") ?? "application/pdf",
        "Content-Disposition": response.headers.get("content-disposition") ?? `attachment; filename=snapshot_${snapshotId}.pdf`,
      },
    });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ message: error.message }, { status: error.status || 500 });
    }

    return NextResponse.json({ message: "Failed to export PDF" }, { status: 500 });
  }
}
