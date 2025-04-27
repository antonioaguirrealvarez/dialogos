"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { InfoIcon } from "lucide-react"
import { useAnalysis } from "../../context/analysis-context"

const depthLevelDescriptions = {
  level_5_feelings_about_relationship: "Discussing feelings about your relationship with the other person",
  level_4_feelings_about_self: "Sharing personal feelings and vulnerabilities",
  level_3_surface: "Discussing personal opinions and thoughts",
  level_2_extended_ritual: "Casual conversation beyond basic pleasantries",
  level_1_ritual: "Basic pleasantries and small talk",
}

// Updated color scheme to use blue for filled portion and light grey for background
const depthLevelColors = {
  level_5_feelings_about_relationship: "bg-blue-600",
  level_4_feelings_about_self: "bg-blue-500",
  level_3_surface: "bg-blue-400",
  level_2_extended_ritual: "bg-blue-300",
  level_1_ritual: "bg-blue-200",
}

export function CommunicationDepth() {
  const { analysis } = useAnalysis()

  if (!analysis) return null

  const depthLevels = [
    {
      key: "level_5_feelings_about_relationship",
      level: "Level 5",
      name: "Feelings about Relationship",
      percentage: Number.parseInt(analysis.communication_depth_distribution.level_5_feelings_about_relationship),
      color: depthLevelColors.level_5_feelings_about_relationship,
      description: depthLevelDescriptions.level_5_feelings_about_relationship,
    },
    {
      key: "level_4_feelings_about_self",
      level: "Level 4",
      name: "Feelings about Self",
      percentage: Number.parseInt(analysis.communication_depth_distribution.level_4_feelings_about_self),
      color: depthLevelColors.level_4_feelings_about_self,
      description: depthLevelDescriptions.level_4_feelings_about_self,
    },
    {
      key: "level_3_surface",
      level: "Level 3",
      name: "Surface",
      percentage: Number.parseInt(analysis.communication_depth_distribution.level_3_surface),
      color: depthLevelColors.level_3_surface,
      description: depthLevelDescriptions.level_3_surface,
    },
    {
      key: "level_2_extended_ritual",
      level: "Level 2",
      name: "Extended Ritual",
      percentage: Number.parseInt(analysis.communication_depth_distribution.level_2_extended_ritual),
      color: depthLevelColors.level_2_extended_ritual,
      description: depthLevelDescriptions.level_2_extended_ritual,
    },
    {
      key: "level_1_ritual",
      level: "Level 1",
      name: "Ritual",
      percentage: Number.parseInt(analysis.communication_depth_distribution.level_1_ritual),
      color: depthLevelColors.level_1_ritual,
      description: depthLevelDescriptions.level_1_ritual,
    },
  ]

  // Calculate the percentage of deeper levels (4-5)
  const deeperLevelsPercentage =
    Number.parseInt(analysis.communication_depth_distribution.level_4_feelings_about_self) +
    Number.parseInt(analysis.communication_depth_distribution.level_5_feelings_about_relationship)

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle>Communication Depth</CardTitle>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <InfoIcon className="h-4 w-4 text-gray-400" />
              </TooltipTrigger>
              <TooltipContent className="max-w-xs">
                <p>Shows the distribution of your conversation across different levels of depth and intimacy.</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
        <CardDescription>Distribution of conversation depth levels</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {depthLevels.map((level) => (
            <div key={level.key} className="space-y-1">
              <div className="flex justify-between text-sm">
                <div className="font-medium">
                  {level.level}: {level.name}
                </div>
                <div className="text-gray-500">{level.percentage}%</div>
              </div>
              <div className="h-3 w-full bg-gray-100 rounded-full overflow-hidden">
                <div className={`h-full ${level.color} rounded-full`} style={{ width: `${level.percentage}%` }}></div>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 text-sm text-gray-500">
          <p>
            Your conversation reached deeper levels (4-5) only {deeperLevelsPercentage}% of the time. Increasing this
            percentage can lead to more meaningful connections.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
