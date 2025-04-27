"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAnalysis } from "../../context/analysis-context"

export function ConversationSummary() {
  const { analysis } = useAnalysis()

  if (!analysis) return null

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle>Conversation Summary</CardTitle>
        <CardDescription>Overview of your conversation context and tone</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-gray-700">{analysis.conversation_summary}</p>
      </CardContent>
    </Card>
  )
}
