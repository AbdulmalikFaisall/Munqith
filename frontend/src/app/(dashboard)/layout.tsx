import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { AppSidebar } from "@/components/layout/app-sidebar";
import { MobileNav } from "@/components/layout/mobile-nav";

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const cookieStore = await cookies();
  const bypass = process.env.NEXT_PUBLIC_DEV_BYPASS_AUTH === "true";
  const token = cookieStore.get("munqith_access_token")?.value;

  if (!bypass && !token) {
    redirect("/login");
  }

  return (
    <div className="min-h-screen bg-[var(--surface)] lg:grid lg:grid-cols-[18rem_1fr]">
      <AppSidebar />
      <div className="min-h-screen pb-16 lg:pb-0">{children}</div>
      <MobileNav />
    </div>
  );
}
