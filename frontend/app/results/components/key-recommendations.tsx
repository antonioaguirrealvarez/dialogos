"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useAnalysis } from "../../context/analysis-context"

export function KeyRecommendations() {
  const { analysis } = useAnalysis()

  if (!analysis) return null

  // Assign priority based on position in the array
  const recommendations = analysis.key_recommendations.map((rec, index) => ({
    id: index + 1,
    title: rec,
    priority: index < 2 ? "High" : "Medium",
  }))

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle>Key Recommendations</CardTitle>
        <CardDescription>Prioritized suggestions to improve your communication effectiveness</CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="space-y-4">
          {recommendations.map((rec) => (
            <li key={rec.id} className="flex gap-3">
              <Badge variant={rec.priority === "High" ? "destructive" : "secondary"} className="mt-1 h-fit">
                {rec.priority}
              </Badge>
              <div>
                <h3 className="font-medium text-gray-900">{rec.title}</h3>
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
