import { MessageSquareText } from "lucide-react"

export function Logo() {
  return (
    <div className="flex items-center gap-2">
      <div className="bg-blue-600 text-white p-2 rounded-lg shadow-lg">
        <MessageSquareText size={24} />
      </div>
      <span className="text-2xl font-bold text-white drop-shadow-md">Dialogos</span>
    </div>
  )
}
