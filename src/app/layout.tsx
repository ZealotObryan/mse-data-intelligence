import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "MSE Analytics | Malawi Market Intelligence", description: "An independent financial data science and market intelligence research prototype focused on the Malawi Stock Exchange." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
