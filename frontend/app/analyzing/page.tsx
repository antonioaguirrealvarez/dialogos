"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Loader2, BarChart2, MessageSquare, Brain } from "lucide-react"
import { useAnalysis } from "../context/analysis-context"
import { AnalysisProgress } from "../components/analysis-progress"

export default function AnalyzingPage() {
  const router = useRouter()
  const { analysis } = useAnalysis()
  const [isJsonUpload, setIsJsonUpload] = useState(false)

  // Determine if this is a JSON upload by checking if the analysis data is already complete
  useEffect(() => {
    if (analysis) {
      // If we have detailed data already, it's likely from a JSON upload
      setIsJsonUpload(true)
    }
  }, [analysis])

  const analysisSteps = isJsonUpload
    ? [
        "Loading JSON data...",
        "Validating analysis format...",
        "Processing visualization data...",
        "Preparing your dashboard...",
      ]
    : [
        "Parsing conversation transcript...",
        "Identifying speakers and topics...",
        "Analyzing communication patterns...",
        "Evaluating emotional expressions...",
        "Measuring conversation depth...",
        "Generating personalized insights...",
        "Preparing your dashboard...",
      ]

  useEffect(() => {
    // If there's no analysis data, redirect back to the upload page
    if (!analysis) {
      router.push("/")
      return
    }

    // Simulate analysis process with a delay
    // Use a shorter delay for JSON uploads since they're already processed
    const timer = setTimeout(
      () => {
        router.push("/results")
      },
      isJsonUpload ? 2000 : 5000,
    )

    return () => clearTimeout(timer)
  }, [analysis, router, isJsonUpload])

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center">
      <div className="max-w-md w-full p-6">
        <div className="flex flex-col items-center text-center space-y-8">
          <div className="relative">
            <div className="absolute inset-0 flex items-center justify-center">
              <Loader2 className="h-16 w-16 text-blue-600 animate-spin" />
            </div>
            <svg className="h-24 w-24" viewBox="0 0 100 100">
              <circle
                className="text-blue-100"
                strokeWidth="4"
                stroke="currentColor"
                fill="transparent"
                r="42"
                cx="50"
                cy="50"
              />
              <circle
                className="text-blue-600"
                strokeWidth="4"
                stroke="currentColor"
                fill="transparent"
                r="42"
                cx="50"
                cy="50"
                strokeDasharray="264"
                strokeDashoffset="110"
                strokeLinecap="round"
              >
                <animateTransform
                  attributeName="transform"
                  type="rotate"
                  from="0 50 50"
                  to="360 50 50"
                  dur="1.5s"
                  repeatCount="indefinite"
                />
              </circle>
            </svg>
          </div>

          <div className="space-y-4">
            <h1 className="text-2xl font-bold text-gray-900">
              {isJsonUpload ? "Loading your analysis" : "Analyzing your conversation"}
            </h1>
            <p className="text-gray-600">
              {isJsonUpload
                ? "We're preparing your dashboard with the uploaded analysis data..."
                : "Our AI is processing your transcript to provide personalized communication insights..."}
            </p>
          </div>

          <div className="w-full">
            <AnalysisProgress steps={analysisSteps} duration={isJsonUpload ? 1800 : 4500} />
          </div>

          <div className="grid grid-cols-3 gap-4 w-full">
            <div className="flex flex-col items-center p-3 bg-white rounded-lg shadow-sm">
              <MessageSquare className="h-6 w-6 text-blue-500 mb-2" />
              <span className="text-sm text-gray-600">{isJsonUpload ? "Loading data" : "Analyzing patterns"}</span>
            </div>
            <div className="flex flex-col items-center p-3 bg-white rounded-lg shadow-sm">
              <Brain className="h-6 w-6 text-blue-500 mb-2" />
              <span className="text-sm text-gray-600">
                {isJsonUpload ? "Processing insights" : "Identifying insights"}
              </span>
            </div>
            <div className="flex flex-col items-center p-3 bg-white rounded-lg shadow-sm">
              <BarChart2 className="h-6 w-6 text-blue-500 mb-2" />
              <span className="text-sm text-gray-600">{isJsonUpload ? "Building visuals" : "Creating metrics"}</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
