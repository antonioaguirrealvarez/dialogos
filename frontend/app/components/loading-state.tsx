"use client"

import { Loader2 } from "lucide-react"

export function LoadingState() {
  return (
    <div className="fixed inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="flex flex-col items-center gap-4 p-4 max-w-md text-center">
        <Loader2 className="h-12 w-12 text-blue-600 animate-spin" />
        <div>
          <h3 className="text-xl font-bold">Analyzing your conversation</h3>
          <p className="text-gray-500 mt-1">
            Our AI is processing your conversation to provide personalized insights...
          </p>
        </div>
      </div>
    </div>
  )
}
