"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { useAnalysis } from "../../context/analysis-context"

export function ProgressMetrics() {
  const { analysis } = useAnalysis()

  if (!analysis) return null

  // Update the metrics parsing to handle the new data format
  const metrics = [
    {
      id: 1,
      title: "Conversation Depth Score",
      description: "Percentage of conversation at levels 4-5 (deeper connection)",
      current:
        Number.parseInt(analysis.communication_depth_distribution.level_4_feelings_about_self) +
        Number.parseInt(analysis.communication_depth_distribution.level_5_feelings_about_relationship),
      target: 40,
      unit: "%",
    },
    {
      id: 2,
      title: "Emotional Awareness",
      description: "Reduction in conversation escalations to anger",
      current: 3, // This would ideally come from the analysis
      target: 1,
      unit: "instances",
    },
    {
      id: 3,
      title: "Conversation Flow",
      description: "Increased use of bridging statements between topics",
      current: 2, // This would ideally come from the analysis
      target: 6,
      unit: "instances",
    },
  ]

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle>Progress Metrics</CardTitle>
        <CardDescription>Key metrics to track your communication improvement</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {metrics.map((metric) => (
            <div key={metric.id} className="space-y-2">
              <div className="flex justify-between items-end">
                <div>
                  <h3 className="font-medium text-gray-900">{metric.title}</h3>
                  <p className="text-sm text-gray-500">{metric.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">
                    {metric.current}
                    <span className="text-sm text-gray-500 ml-1">{metric.unit}</span>
                  </div>
                  <p className="text-sm text-gray-500">
                    Target: {metric.target}
                    {metric.unit}
                  </p>
                </div>
              </div>
              <Progress value={(metric.current / metric.target) * 100} max={200} className="h-2" />
            </div>
          ))}
        </div>
        <div className="mt-6 text-sm text-gray-600">
          <p>
            Track these metrics over time to measure your progress. We recommend analyzing at least one conversation per
            week for optimal improvement.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
