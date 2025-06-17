import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "../../lib/auth-context";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "MindMirror - The Journal That Thinks With You",
  description: "Self-aware journaling companion powered by advanced AI. Turn your thoughts into insights, patterns into breakthroughs, and questions into clarity.",
  keywords: ["journaling", "AI", "self-reflection", "mindfulness", "personal growth", "Swae OS"],
  authors: [{ name: "Swae OS Team" }],
  openGraph: {
    title: "MindMirror - The Journal That Thinks With You",
    description: "Self-aware journaling companion powered by advanced AI",
    url: "https://mindmirror.swae.io",
    siteName: "MindMirror",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "MindMirror - The Journal That Thinks With You",
    description: "Self-aware journaling companion powered by advanced AI",
  },
  viewport: "width=device-width, initial-scale=1",
  robots: "index, follow",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
