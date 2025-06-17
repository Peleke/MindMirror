'use client'

import { MessageCircle } from 'lucide-react'

export default function ChatPage() {
  return (
    <div className="p-6 max-w-4xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <MessageCircle className="w-8 h-8 text-blue-500" />
          <h1 className="text-3xl font-bold text-gray-900">AI Chat</h1>
        </div>
        <p className="text-gray-600">
          Converse with your intelligent AI companion.
        </p>
      </div>

      <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Coming Soon
        </h2>
        <p className="text-gray-600">
          The AI chat interface will be implemented in the next phase. 
          This will include real-time conversation with your AI companion, 
          message history, and tradition-aware responses.
        </p>
      </div>
    </div>
  )
} 