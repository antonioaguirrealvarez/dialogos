"use client"

import { useState, useEffect } from "react"

interface AnalysisProgressProps {
  steps: string[]
  duration: number
}

export function AnalysisProgress({ steps, duration }: AnalysisProgressProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const stepDuration = duration / steps.length

  useEffect(() => {
    if (currentStep >= steps.length) return

    const timer = setTimeout(() => {
      setCurrentStep((prev) => prev + 1)
    }, stepDuration)

    return () => clearTimeout(timer)
  }, [currentStep, stepDuration, steps.length])

  return (
    <div className="w-full space-y-2">
      <div className="h-2 bg-blue-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-600 transition-all duration-300 ease-in-out"
          style={{ width: `${(currentStep / steps.length) * 100}%` }}
        ></div>
      </div>
      <div className="text-sm text-blue-600 font-medium">
        {currentStep < steps.length ? steps[currentStep] : "Analysis complete!"}
      </div>
    </div>
  )
}
