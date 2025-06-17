'use client'

import { Heart } from 'lucide-react'

export default function GratitudePage() {
  return (
    <div className="p-6 max-w-4xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Heart className="w-8 h-8 text-red-500" />
          <h1 className="text-3xl font-bold text-gray-900">Morning Gratitude</h1>
        </div>
        <p className="text-gray-600">
          Start your day by reflecting on what you're grateful for.
        </p>
      </div>

      <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Coming Soon
        </h2>
        <p className="text-gray-600">
          The gratitude journaling form will be implemented in the next phase. 
          This will include fields for three things you're grateful for, 
          three things you're excited about, focus areas, and mood tracking.
        </p>
      </div>
    </div>
  )
} 