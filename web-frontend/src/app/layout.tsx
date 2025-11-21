import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";
import { LocaleProvider } from "@/providers/LocaleProvider";

export const metadata: Metadata = {
  title: "test.me - AI Exam Platform",
  description: "AI-powered exam generation and grading platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="antialiased">
        <LocaleProvider>
          {children}
          <Toaster />
        </LocaleProvider>
      </body>
    </html>
  );
}

