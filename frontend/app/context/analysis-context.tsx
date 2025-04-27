"use client"

import React, { createContext, useContext, type ReactNode } from "react"
import type { ConversationAnalysis } from "../types/analysis"

interface AnalysisContextType {
  analysis: ConversationAnalysis | null
  setAnalysis: (analysis: ConversationAnalysis) => void
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined)

export function AnalysisProvider({
  children,
  initialData = null,
}: { children: ReactNode; initialData?: ConversationAnalysis | null }) {
  const [analysis, setAnalysis] = React.useState<ConversationAnalysis | null>(initialData)

  return <AnalysisContext.Provider value={{ analysis, setAnalysis }}>{children}</AnalysisContext.Provider>
}

export function useAnalysis() {
  const context = useContext(AnalysisContext)
  if (context === undefined) {
    throw new Error("useAnalysis must be used within an AnalysisProvider")
  }
  return context
}
