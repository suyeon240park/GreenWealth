import type React from "react"
import "@/app/globals.css"
import { Inter } from "next/font/google"
import type { Metadata } from "next"
import { cn } from "@/lib/utils"
import { ThemeProvider } from "@/components/theme-provider"
import { PlaidProvider } from "../lib/plaid-context"
import Link from "next/link"
import { Leaf } from "lucide-react"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "EcoFinance Advisor",
  description: "AI-powered personal finance and sustainability advisor",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={cn("min-h-screen bg-background font-sans antialiased", inter.className)}>
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
          <PlaidProvider>
            <div className="flex min-h-screen flex-col">
              <header className="border-b">
                <div className="flex h-16 items-center px-4">
                  <Link href="/" className="flex items-center gap-2">
                    <Leaf className="h-6 w-6 text-green-500" />
                    <span className="text-lg font-bold">EcoFinance</span>
                  </Link>
                </div>
              </header>
              <div className="flex-1">{children}</div>
            </div>
          </PlaidProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}

