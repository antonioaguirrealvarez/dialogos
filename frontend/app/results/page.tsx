"use client"
import { Logo } from "../components/logo"
import { ConversationSummary } from "./components/conversation-summary"
import { CommunicationDepth } from "./components/communication-depth"
import { CommunicationRadar } from "./components/communication-radar"
import { StrengthGrowth } from "./components/strength-growth"
import { KeyRecommendations } from "./components/key-recommendations"
import { DetailedRecommendations } from "./components/detailed-recommendations"
import { StrengthsAssessment } from "./components/strengths-assessment"
import { ProgressMetrics } from "./components/progress-metrics"
import { EmotionTimeline } from "./components/emotion-timeline"
import { Button } from "@/components/ui/button"
import { Download, Share2 } from "lucide-react"
import { useAnalysis } from "../context/analysis-context"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function ResultsPage() {
  const { analysis } = useAnalysis()
  const router = useRouter()

  // If there's no analysis data, redirect back to the upload page
  useEffect(() => {
    if (!analysis) {
      router.push("/")
    }
  }, [analysis, router])

  if (!analysis) {
    return null
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white pb-16">
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <Logo />
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="flex items-center gap-1">
              <Download className="h-4 w-4" />
              <span className="hidden sm:inline">Export</span>
            </Button>
            <Button variant="outline" size="sm" className="flex items-center gap-1">
              <Share2 className="h-4 w-4" />
              <span className="hidden sm:inline">Share</span>
            </Button>
            <Button size="sm" onClick={() => router.push("/")}>
              New Analysis
            </Button>
          </div>
        </div>
      </header>

      <div className="container max-w-6xl mx-auto px-4 py-8 space-y-10">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-gray-900">Your Conversation Analysis</h1>
          <p className="text-gray-600">Analysis completed on {new Date().toLocaleDateString()}</p>
        </div>

        <ConversationSummary />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <CommunicationDepth />
          <CommunicationRadar />
        </div>

        {/* Add the new Emotion Timeline component after the Communication Depth */}
        {analysis.emotion_analysis && analysis.emotion_analysis.length > 0 && <EmotionTimeline />}

        <StrengthGrowth />

        <KeyRecommendations />

        <DetailedRecommendations />

        <StrengthsAssessment />

        <ProgressMetrics />
      </div>
    </main>
  )
}
