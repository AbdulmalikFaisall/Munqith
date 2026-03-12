import { NextRequest, NextResponse } from "next/server";

import { ApiError } from "@/lib/api/errors";
import { loginWithBackend } from "@/lib/api/auth";
import { LoginRequestDto } from "@/lib/api/types";
import { parseExpiryFromToken, parseRoleFromToken } from "@/lib/auth/jwt";

const ACCESS_COOKIE = "munqith_access_token";
const ROLE_COOKIE = "munqith_user_role";

export async function POST(request: NextRequest) {
  let payload: LoginRequestDto;

  try {
    payload = (await request.json()) as LoginRequestDto;
  } catch {
    return NextResponse.json({ message: "Invalid JSON payload" }, { status: 400 });
  }

  if (!payload?.email || !payload?.password) {
    return NextResponse.json({ message: "Email and password are required" }, { status: 400 });
  }

  try {
    const result = await loginWithBackend(payload);
    const role = parseRoleFromToken(result.access_token);
    const expiresAtMs = parseExpiryFromToken(result.access_token);

    const response = NextResponse.json(
      {
        authenticated: true,
        role,
      },
      { status: 200 },
    );

    response.cookies.set(ACCESS_COOKIE, result.access_token, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      expires: expiresAtMs ? new Date(expiresAtMs) : undefined,
    });

    if (role) {
      response.cookies.set(ROLE_COOKIE, role, {
        httpOnly: true,
        sameSite: "lax",
        secure: process.env.NODE_ENV === "production",
        path: "/",
        expires: expiresAtMs ? new Date(expiresAtMs) : undefined,
      });
    }

    return response;
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ message: error.message }, { status: error.status || 500 });
    }

    return NextResponse.json({ message: "Login failed" }, { status: 500 });
  }
}
