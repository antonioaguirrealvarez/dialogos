"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { useAnalysis } from "../../context/analysis-context"

export function DetailedRecommendations() {
  const { analysis } = useAnalysis()

  if (!analysis) return null

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle>Detailed Recommendations</CardTitle>
        <CardDescription>In-depth analysis and actionable advice for improving your communication</CardDescription>
      </CardHeader>
      <CardContent>
        <Accordion type="single" collapsible className="w-full">
          {analysis.detailed_recommendations.map((rec, index) => (
            <AccordionItem key={`rec-${index}`} value={`rec-${index}`}>
              <AccordionTrigger className="text-left font-medium">{rec.title}</AccordionTrigger>
              <AccordionContent>
                <div className="space-y-4 pt-2">
                  <div>
                    <h4 className="font-medium text-gray-900">Current Pattern</h4>
                    <p className="text-gray-600">{rec.current_pattern}</p>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900">Improvement Opportunity</h4>
                    <p className="text-gray-600">{rec.improvement_opportunity}</p>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900">Example Reframing</h4>
                    <div className="mt-2 space-y-2">
                      <div className="bg-gray-100 p-3 rounded-md">
                        <p className="text-sm font-medium text-gray-500">Before:</p>
                        <p className="text-gray-700 italic">"{rec.example_reframing.before}"</p>
                      </div>
                      <div className="bg-blue-50 p-3 rounded-md">
                        <p className="text-sm font-medium text-blue-500">After:</p>
                        <p className="text-gray-700 italic">"{rec.example_reframing.after}"</p>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900">Benefits</h4>
                    <p className="text-gray-600">{rec.benefits}</p>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900">Practice Suggestion</h4>
                    <p className="text-gray-600">{rec.practice_suggestion}</p>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </CardContent>
    </Card>
  )
}
