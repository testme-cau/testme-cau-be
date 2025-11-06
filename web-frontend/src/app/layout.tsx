import type { Metadata } from "next";
import "./globals.css";

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
        {children}
      </body>
    </html>
  );
}

