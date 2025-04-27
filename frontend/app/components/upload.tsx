"use client"

import type React from "react"

import { useState } from "react"
import { UploadIcon, Mic, FileText, ArrowRight, Code } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useRouter } from "next/navigation"
import { useAnalysis } from "../context/analysis-context"
import type { ConversationAnalysis, EmotionAnalysis } from "../types/analysis"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

// Sample analysis data
const sampleAnalysisData: ConversationAnalysis = {
  conversation_summary:
    "Brief conversation between three speakers in a hackathon setting, moving from enthusiasm to expressions of anger and frustration, then discussing Speaker_1's roommate with apprehension. The tone shifts erratically from excitement to confrontation to uncertainty.",
  communication_depth_distribution: {
    level_1_ritual: "15%",
    level_2_extended_ritual: "20%",
    level_3_surface: "30%",
    level_4_feelings_about_self: "30%",
    level_5_feelings_about_relationship: "5%",
  },
  pentagonal_radar_assessment: {
    self_disclosure: 6,
    emotional_expression: 4,
    active_listening: 3,
    attribution_accuracy: 5,
    conversation_balance: 4,
  },
  strengths_and_growth: {
    strengths: [
      "Direct emotional expression: 'I'm getting like really fucking angry with you'",
      "Self-disclosure about current feelings: 'I don't think I'm very happy'",
      "Acknowledging others' emotional states: 'You sound apprehensive'",
    ],
    growth_opportunities: [
      "Emotional regulation: The quick escalation to anger shows opportunity for better regulation",
      "Transition management: Abrupt topic shifts created disconnection",
      "Congruent communication: Mismatch between 'best day ever' and subsequent hostility",
      "Curiosity vs. dismissal: Shutting down negative emotions rather than exploring them",
    ],
  },
  key_recommendations: [
    "Practice emotional awareness before expression",
    "Develop bridging statements for smoother conversations",
    "Increase curiosity about others' experiences",
    "Balance authenticity with appropriate boundaries",
  ],
  detailed_recommendations: [
    {
      title: "Practice emotional awareness before expression",
      current_pattern: "Emotions emerge explosively with little filtering or processing",
      improvement_opportunity:
        "Create space between feeling an emotion and expressing it, allowing for more measured responses",
      example_reframing: {
        before: "Dude, you're really changing my mood. I'm getting like really fucking angry with you",
        after:
          "I notice I'm feeling frustrated because I came in feeling excited and now I'm hearing some difficult things from you.",
      },
      benefits: "Prevents escalation, maintains connection even during disagreement, and models emotional intelligence",
      practice_suggestion:
        "Before responding to something triggering, take a breath and mentally complete: 'I'm feeling _____ because _____'",
    },
  ],
  strengths_assessment: [
    {
      strength: "Direct emotional expression",
      effectiveness: "Provides clarity about internal state and creates opportunity for authentic dialogue",
      leverage: "Maintain directness while adding nuance about the source of emotions",
    },
  ],
  progress_metrics: [
    "Reduction in conversation escalations to anger",
    "Increased use of bridging statements between topics",
    "More follow-up questions when others share difficult emotions",
  ],
  // Sample emotion analysis data
  emotion_analysis: [
    { speaker: "spk_0", quintile: 1, main_emotion: "Awe" },
    { speaker: "spk_0", quintile: 2, main_emotion: "Joy" },
    { speaker: "spk_0", quintile: 3, main_emotion: "Anger" },
    { speaker: "spk_0", quintile: 4, main_emotion: "Doubt" },
    { speaker: "spk_0", quintile: 5, main_emotion: "Sadness" },
    { speaker: "spk_1", quintile: 1, main_emotion: "Distress" },
    { speaker: "spk_1", quintile: 2, main_emotion: "Distress" },
    { speaker: "spk_1", quintile: 3, main_emotion: "Anger" },
    { speaker: "spk_1", quintile: 4, main_emotion: "Happiness" },
    { speaker: "spk_1", quintile: 5, main_emotion: "Joy" },
  ],
}

export function Upload() {
  const router = useRouter()
  const { setAnalysis } = useAnalysis()
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [jsonFile, setJsonFile] = useState<File | null>(null)
  const [emotionJsonFile, setEmotionJsonFile] = useState<File | null>(null)
  const [transcript, setTranscript] = useState("")
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAudioUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setAudioFile(file)
  }

  const handleJsonUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setJsonFile(file)
    setError(null) // Clear any previous errors
  }

  const handleEmotionJsonUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setEmotionJsonFile(file)
  }

  const handleTranscriptChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setTranscript(e.target.value)
  }

  const validateJsonData = (data: any): data is ConversationAnalysis => {
    // Basic validation to ensure the JSON has the required structure
    if (!data) return false

    const requiredFields = [
      "conversation_summary",
      "communication_depth_distribution",
      "pentagonal_radar_assessment",
      "strengths_and_growth",
      "key_recommendations",
      "detailed_recommendations",
      "strengths_assessment",
      "progress_metrics",
    ]

    for (const field of requiredFields) {
      if (!data[field]) return false
    }

    // Check depth distribution fields
    const depthFields = [
      "level_1_ritual",
      "level_2_extended_ritual",
      "level_3_surface",
      "level_4_feelings_about_self",
      "level_5_feelings_about_relationship",
    ]

    for (const field of depthFields) {
      if (!data.communication_depth_distribution[field]) return false
    }

    // Check radar assessment fields
    const radarFields = [
      "self_disclosure",
      "emotional_expression",
      "active_listening",
      "attribution_accuracy",
      "conversation_balance",
    ]

    for (const field of radarFields) {
      if (typeof data.pentagonal_radar_assessment[field] !== "number") return false
    }

    return true
  }

  const validateEmotionData = (data: any): data is EmotionAnalysis[] => {
    if (!Array.isArray(data)) return false

    // Check if each item has the required structure
    return data.every(
      (item) =>
        typeof item.speaker === "string" && typeof item.quintile === "number" && typeof item.main_emotion === "string",
    )
  }

  const handleSubmit = async (type: "audio" | "transcript" | "json") => {
    setIsUploading(true)
    setError(null)

    try {
      if (type === "json" && jsonFile) {
        // Read and parse the JSON file
        const fileContent = await jsonFile.text()
        let jsonData

        try {
          jsonData = JSON.parse(fileContent)
        } catch (e) {
          throw new Error("Invalid JSON format. Please check your file and try again.")
        }

        // Validate the JSON structure
        if (!validateJsonData(jsonData)) {
          throw new Error("The JSON file doesn't match the required format. Please check the structure and try again.")
        }

        // If we have an emotion JSON file, read and parse it too
        if (emotionJsonFile) {
          try {
            const emotionContent = await emotionJsonFile.text()
            const emotionData = JSON.parse(emotionContent)

            if (validateEmotionData(emotionData)) {
              // Add the emotion data to the main JSON data
              jsonData.emotion_analysis = emotionData
            } else {
              console.warn("Emotion data format is invalid. Using without emotion analysis.")
            }
          } catch (e) {
            console.warn("Could not parse emotion JSON file. Using without emotion analysis.")
          }
        }

        // Use the data from the JSON file
        setAnalysis(jsonData)
      } else {
        // For audio and transcript, use the sample data
        setAnalysis(sampleAnalysisData)
      }

      // Navigate to the analyzing page
      router.push("/analyzing")
    } catch (error) {
      console.error("Upload error:", error)
      setError(error instanceof Error ? error.message : "An unknown error occurred")
      setIsUploading(false)
    }
  }

  return (
    <Card className="w-full bg-white/95 backdrop-blur-sm shadow-xl">
      <CardHeader>
        <CardTitle>Upload your conversation</CardTitle>
        <CardDescription>Upload an audio recording, paste a transcript, or upload a JSON analysis file</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="audio" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="audio" className="flex items-center gap-2">
              <Mic className="h-4 w-4" />
              <span>Audio</span>
            </TabsTrigger>
            <TabsTrigger value="transcript" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <span>Transcript</span>
            </TabsTrigger>
            <TabsTrigger value="json" className="flex items-center gap-2">
              <Code className="h-4 w-4" />
              <span>JSON</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="audio" className="mt-4">
            <div className="space-y-4">
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="audio-upload">Upload audio file</Label>
                <div className="flex items-center justify-center w-full">
                  <label
                    htmlFor="audio-upload"
                    className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100"
                  >
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <UploadIcon className="w-8 h-8 mb-3 text-gray-400" />
                      <p className="mb-2 text-sm text-gray-500">
                        <span className="font-semibold">Click to upload</span> or drag and drop
                      </p>
                      <p className="text-xs text-gray-500">MP3, WAV, or M4A (max. 60 minutes)</p>
                    </div>
                    <input
                      id="audio-upload"
                      type="file"
                      className="hidden"
                      accept="audio/*"
                      onChange={handleAudioUpload}
                    />
                  </label>
                </div>
                {audioFile && <p className="text-sm text-gray-500">Selected: {audioFile.name}</p>}
              </div>

              <Button className="w-full" disabled={!audioFile || isUploading} onClick={() => handleSubmit("audio")}>
                {isUploading ? "Uploading..." : "Analyze Audio"}
                {!isUploading && <ArrowRight className="ml-2 h-4 w-4" />}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="transcript" className="mt-4">
            <div className="space-y-4">
              <div className="grid w-full gap-1.5">
                <Label htmlFor="transcript">Paste your conversation transcript</Label>
                <Textarea
                  id="transcript"
                  placeholder="Paste your conversation here..."
                  className="min-h-[150px]"
                  value={transcript}
                  onChange={handleTranscriptChange}
                />
              </div>

              <Button
                className="w-full"
                disabled={!transcript.trim() || isUploading}
                onClick={() => handleSubmit("transcript")}
              >
                {isUploading ? "Analyzing..." : "Analyze Transcript"}
                {!isUploading && <ArrowRight className="ml-2 h-4 w-4" />}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="json" className="mt-4">
            <div className="space-y-4">
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="json-upload">Upload analysis JSON file</Label>
                <div className="flex items-center justify-center w-full">
                  <label
                    htmlFor="json-upload"
                    className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100"
                  >
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <UploadIcon className="w-8 h-8 mb-3 text-gray-400" />
                      <p className="mb-2 text-sm text-gray-500">
                        <span className="font-semibold">Click to upload</span> or drag and drop
                      </p>
                      <p className="text-xs text-gray-500">JSON file with conversation analysis data</p>
                    </div>
                    <input
                      id="json-upload"
                      type="file"
                      className="hidden"
                      accept="application/json"
                      onChange={handleJsonUpload}
                    />
                  </label>
                </div>
                {jsonFile && <p className="text-sm text-gray-500">Selected: {jsonFile.name}</p>}
              </div>

              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="emotion-json-upload">Upload emotion analysis JSON (optional)</Label>
                <div className="flex items-center justify-center w-full">
                  <label
                    htmlFor="emotion-json-upload"
                    className="flex flex-col items-center justify-center w-full h-24 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100"
                  >
                    <div className="flex flex-col items-center justify-center pt-3 pb-4">
                      <UploadIcon className="w-6 h-6 mb-2 text-gray-400" />
                      <p className="text-xs text-gray-500">Emotion analysis JSON file (optional)</p>
                    </div>
                    <input
                      id="emotion-json-upload"
                      type="file"
                      className="hidden"
                      accept="application/json"
                      onChange={handleEmotionJsonUpload}
                    />
                  </label>
                </div>
                {emotionJsonFile && <p className="text-sm text-gray-500">Selected: {emotionJsonFile.name}</p>}
              </div>

              {error && (
                <Alert variant="destructive" className="mt-2">
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button className="w-full" disabled={!jsonFile || isUploading} onClick={() => handleSubmit("json")}>
                {isUploading ? "Processing..." : "Load JSON Analysis"}
                {!isUploading && <ArrowRight className="ml-2 h-4 w-4" />}
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
      <CardFooter className="flex justify-center border-t pt-4">
        <p className="text-xs text-center text-gray-500">
          By uploading, you agree to our{" "}
          <a href="#" className="underline">
            Terms of Service
          </a>{" "}
          and{" "}
          <a href="#" className="underline">
            Privacy Policy
          </a>
        </p>
      </CardFooter>
    </Card>
  )
}
