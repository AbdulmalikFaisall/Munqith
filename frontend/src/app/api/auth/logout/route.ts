import { NextResponse } from "next/server";

const ACCESS_COOKIE = "munqith_access_token";
const ROLE_COOKIE = "munqith_user_role";

export async function POST() {
  const response = NextResponse.json({ authenticated: false }, { status: 200 });

  response.cookies.set(ACCESS_COOKIE, "", {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    expires: new Date(0),
  });

  response.cookies.set(ROLE_COOKIE, "", {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    expires: new Date(0),
  });

  return response;
}
