"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CheckCircle2, ArrowUpCircle } from "lucide-react"
import { useAnalysis } from "../../context/analysis-context"

export function StrengthGrowth() {
  const { analysis } = useAnalysis()

  if (!analysis) return null

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle>Strengths & Growth Opportunities</CardTitle>
        <CardDescription>Specific communication patterns identified in your conversation</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="strengths" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger value="strengths" className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" />
              <span>What You Did Well</span>
            </TabsTrigger>
            <TabsTrigger value="growth" className="flex items-center gap-2">
              <ArrowUpCircle className="h-4 w-4" />
              <span>Growth Opportunities</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="strengths" className="space-y-4">
            {analysis.strengths_and_growth.strengths.map((strength, index) => {
              // Extract the title and example from the strength string
              const colonIndex = strength.indexOf(":")
              const title = colonIndex > -1 ? strength.substring(0, colonIndex) : "Strength"
              const example = colonIndex > -1 ? strength.substring(colonIndex + 1).trim() : strength

              return (
                <div key={index} className="space-y-2">
                  <h3 className="font-medium text-blue-700">{title}</h3>
                  <p className="text-gray-700">{example}</p>
                </div>
              )
            })}
          </TabsContent>

          <TabsContent value="growth" className="space-y-4">
            {analysis.strengths_and_growth.growth_opportunities.map((growth, index) => {
              // Extract the title and example from the growth string
              const colonIndex = growth.indexOf(":")
              const title = colonIndex > -1 ? growth.substring(0, colonIndex) : "Growth Area"
              const example = colonIndex > -1 ? growth.substring(colonIndex + 1).trim() : growth

              return (
                <div key={index} className="space-y-2">
                  <h3 className="font-medium text-amber-700">{title}</h3>
                  <p className="text-gray-700">{example}</p>
                </div>
              )
            })}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
