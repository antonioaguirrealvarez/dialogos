"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAnalysis } from "../../context/analysis-context"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

// Define emotion colors for visualization
const emotionColors: Record<string, { bg: string; text: string }> = {
  Joy: { bg: "bg-yellow-100", text: "text-yellow-800" },
  Happiness: { bg: "bg-yellow-100", text: "text-yellow-800" },
  Awe: { bg: "bg-purple-100", text: "text-purple-800" },
  Anger: { bg: "bg-red-100", text: "text-red-800" },
  Distress: { bg: "bg-orange-100", text: "text-orange-800" },
  Doubt: { bg: "bg-blue-100", text: "text-blue-800" },
  Sadness: { bg: "bg-blue-100", text: "text-blue-800" },
  // Add more emotions as needed
}

// Helper function to get a default color for emotions not in our map
const getEmotionColor = (emotion: string) => {
  return emotionColors[emotion] || { bg: "bg-gray-100", text: "text-gray-800" }
}

// Helper function to get a speaker name
const getSpeakerName = (speakerId: string) => {
  const speakerNumber = speakerId.replace("spk_", "")
  return `Speaker ${Number.parseInt(speakerNumber) + 1}`
}

export function EmotionTimeline() {
  const { analysis } = useAnalysis()

  if (!analysis || !analysis.emotion_analysis || analysis.emotion_analysis.length === 0) {
    return null
  }

  // Get unique speakers
  const speakers = [...new Set(analysis.emotion_analysis.map((item) => item.speaker))]

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle>Emotional Journey</CardTitle>
        <CardDescription>How emotions evolved throughout the conversation</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue={speakers[0]} className="w-full">
          <TabsList className="grid w-full" style={{ gridTemplateColumns: `repeat(${speakers.length}, 1fr)` }}>
            {speakers.map((speaker) => (
              <TabsTrigger key={speaker} value={speaker}>
                {getSpeakerName(speaker)}
              </TabsTrigger>
            ))}
          </TabsList>

          {speakers.map((speaker) => (
            <TabsContent key={speaker} value={speaker} className="mt-4">
              <div className="space-y-6">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <h3 className="text-lg font-medium">{getSpeakerName(speaker)}'s Emotional Journey</h3>
                  <div className="flex flex-wrap gap-2">
                    {analysis.emotion_analysis
                      .filter((item) => item.speaker === speaker)
                      .map((item) => {
                        const { bg, text } = getEmotionColor(item.main_emotion)
                        return (
                          <Badge key={item.quintile} variant="outline" className={`${bg} ${text}`}>
                            {item.main_emotion}
                          </Badge>
                        )
                      })}
                  </div>
                </div>

                <div className="relative">
                  <div className="absolute top-0 left-0 w-full h-0.5 bg-gray-200"></div>
                  <div className="flex justify-between mt-4">
                    {[1, 2, 3, 4, 5].map((quintile) => (
                      <div key={quintile} className="flex-1 text-center">
                        <div className="relative">
                          <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-4 w-0.5 h-3 bg-gray-200"></div>
                        </div>
                        <div className="mt-2 text-xs text-gray-500">Segment {quintile}</div>
                      </div>
                    ))}
                  </div>

                  <div className="mt-4 flex justify-between">
                    {analysis.emotion_analysis
                      .filter((item) => item.speaker === speaker)
                      .sort((a, b) => a.quintile - b.quintile)
                      .map((item, index, array) => {
                        const { bg, text } = getEmotionColor(item.main_emotion)
                        const isFirst = index === 0
                        const isLast = index === array.length - 1
                        const prevEmotion = !isFirst ? array[index - 1].main_emotion : null

                        return (
                          <div key={item.quintile} className="flex-1 flex flex-col items-center">
                            <div
                              className={`w-12 h-12 rounded-full flex items-center justify-center ${bg} ${text} relative`}
                            >
                              {!isFirst && (
                                <div
                                  className="absolute right-full top-1/2 h-0.5 bg-gray-200"
                                  style={{ width: "calc(100% - 1.5rem)" }}
                                ></div>
                              )}
                              <span className="text-xs font-medium">{item.main_emotion.substring(0, 3)}</span>
                            </div>
                            {prevEmotion !== item.main_emotion && !isFirst && (
                              <div className="mt-1 text-xs text-gray-500">
                                {prevEmotion} → {item.main_emotion}
                              </div>
                            )}
                          </div>
                        )
                      })}
                  </div>
                </div>

                <div className="mt-6 space-y-4">
                  <h4 className="font-medium">Emotional Patterns</h4>
                  <div className="text-sm text-gray-700">
                    {(() => {
                      const emotions = analysis.emotion_analysis
                        .filter((item) => item.speaker === speaker)
                        .map((item) => item.main_emotion)

                      // Check for emotional shifts
                      const hasNegativeShift = emotions.some((e) => ["Anger", "Distress", "Sadness"].includes(e))
                      const endsPositive = ["Joy", "Happiness", "Awe"].includes(emotions[emotions.length - 1])
                      const startsPositive = ["Joy", "Happiness", "Awe"].includes(emotions[0])

                      if (hasNegativeShift && endsPositive) {
                        return `${getSpeakerName(speaker)} experienced emotional turbulence but ended the conversation in a positive emotional state.`
                      } else if (startsPositive && !endsPositive) {
                        return `${getSpeakerName(speaker)} began with positive emotions but shifted to more complex feelings as the conversation progressed.`
                      } else if (!startsPositive && !endsPositive) {
                        return `${getSpeakerName(speaker)} maintained predominantly challenging emotions throughout the conversation.`
                      } else {
                        return `${getSpeakerName(speaker)}'s emotional state remained relatively consistent throughout the conversation.`
                      }
                    })()}
                  </div>
                </div>
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </CardContent>
    </Card>
  )
}
