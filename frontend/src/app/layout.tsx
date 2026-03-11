import type { Metadata } from "next";
import { Cairo, IBM_Plex_Mono } from "next/font/google";

import { QueryProvider } from "@/components/providers/query-provider";

import "./globals.css";

const cairo = Cairo({
  variable: "--font-cairo",
  subsets: ["latin"],
});

const ibmPlexMono = IBM_Plex_Mono({
  variable: "--font-ibm-plex-mono",
  weight: ["400", "500"],
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Munqith | Financial Intelligence Dashboard",
  description: "Deterministic startup intelligence platform for KSA companies.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${cairo.variable} ${ibmPlexMono.variable} antialiased`}>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
