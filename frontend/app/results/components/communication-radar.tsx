"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts"
import { ChartContainer } from "@/components/ui/chart"
import { useAnalysis } from "../../context/analysis-context"

export function CommunicationRadar() {
  const { analysis } = useAnalysis()

  if (!analysis) return null

  const radarData = [
    {
      subject: "Self-disclosure",
      score: analysis.pentagonal_radar_assessment.self_disclosure,
      fullMark: 10,
    },
    {
      subject: "Emotional expression",
      score: analysis.pentagonal_radar_assessment.emotional_expression,
      fullMark: 10,
    },
    {
      subject: "Active listening",
      score: analysis.pentagonal_radar_assessment.active_listening,
      fullMark: 10,
    },
    {
      subject: "Attribution accuracy",
      score: analysis.pentagonal_radar_assessment.attribution_accuracy,
      fullMark: 10,
    },
    {
      subject: "Conversation balance",
      score: analysis.pentagonal_radar_assessment.conversation_balance,
      fullMark: 10,
    },
  ]

  // Find strengths (scores >= 6)
  const strengths = radarData
    .filter((item) => item.score >= 6)
    .map((item) => `${item.subject} (${item.score}/10)`)
    .join(", ")

  // Find growth areas (scores <= 4)
  const growthAreas = radarData
    .filter((item) => item.score <= 4)
    .map((item) => `${item.subject} (${item.score}/10)`)
    .join(", ")

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle>Communication Dimensions</CardTitle>
        <CardDescription>Assessment of your communication skills across five key dimensions</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex justify-center w-full">
          <ChartContainer
            config={{
              score: {
                label: "Your Score",
                color: "hsl(var(--chart-1))",
              },
            }}
            className="h-[300px] w-full max-w-[500px]"
          >
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%">
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12 }} />
                <PolarRadiusAxis angle={90} domain={[0, 10]} />
                <Radar
                  name="Score"
                  dataKey="score"
                  data={radarData}
                  stroke="var(--color-score)"
                  fill="var(--color-score)"
                  fillOpacity={0.6}
                />
              </RadarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </div>
        <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="font-medium">Strengths:</p>
            <p className="text-gray-600">{strengths || "None identified"}</p>
          </div>
          <div>
            <p className="font-medium">Growth areas:</p>
            <p className="text-gray-600">{growthAreas || "None identified"}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
