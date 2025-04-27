import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { AnalysisProvider } from "./context/analysis-context"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Dialogos - Form better connections",
  description:
    "An AI-powered communication coach that provides personalized, real-time insights to help you develop deeper connections through more meaningful conversations.",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
          <AnalysisProvider>{children}</AnalysisProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
