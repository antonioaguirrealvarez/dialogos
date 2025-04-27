"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAnalysis } from "../../context/analysis-context"

export function StrengthsAssessment() {
  const { analysis } = useAnalysis()

  if (!analysis) return null

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle>Strengths Assessment</CardTitle>
        <CardDescription>Positive communication patterns you demonstrated</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {analysis.strengths_assessment.map((strength, index) => (
            <div key={index} className="space-y-3">
              <h3 className="text-lg font-medium text-blue-700">{strength.strength}</h3>

              <div>
                <h4 className="text-sm font-medium text-gray-700">Why it was effective</h4>
                <p className="text-gray-600">{strength.effectiveness}</p>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700">How to leverage this strength</h4>
                <p className="text-gray-600">{strength.leverage}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
