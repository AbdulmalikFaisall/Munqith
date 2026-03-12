import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { SessionDto } from "@/lib/api/types";
import { parseExpiryFromToken } from "@/lib/auth/jwt";

const ACCESS_COOKIE = "munqith_access_token";
const ROLE_COOKIE = "munqith_user_role";

export async function GET() {
  const cookieStore = await cookies();
  const token = cookieStore.get(ACCESS_COOKIE)?.value;
  const role = cookieStore.get(ROLE_COOKIE)?.value ?? null;

  const session: SessionDto = {
    authenticated: Boolean(token),
    role: role === "ANALYST" || role === "ADMIN" ? role : null,
    tokenExpiresAtEpochMs: token ? parseExpiryFromToken(token) : null,
  };

  return NextResponse.json(session, { status: 200 });
}
