'use client'

import { ChatInterface } from '../../../components/chat/ChatInterface'

export default function ChatPage() {
  return (
    <div className="p-6 h-full">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Companion</h1>
        <p className="text-gray-600">
          Chat with your AI companion for guidance, reflection, and support on your journey.
        </p>
      </div>
      
      <ChatInterface />
    </div>
  )
} 